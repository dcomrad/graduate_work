import logging
from typing import Any

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = Any


class CRUDBase:
    def __init__(self, model: Any, logger: logging.Logger):
        self.model = model
        self.logger = logger

    async def get(
            self,
            session: AsyncSession,
            attrs: dict[str, Any]
    ):
        if len(attrs) == 0:
            raise ValueError('There should be at least one key=value variable')

        db_obj = await session.execute(self._make_query(attrs))
        return db_obj.scalars().first()

    async def get_all(
            self,
            session: AsyncSession,
            attrs: dict[str, Any] | None = None,
            *,
            limit: int | None = None,
            offset: int | None = None,
            sort: str | None = None,
    ):
        db_objs = await session.execute(
            self._make_query(attrs, limit=limit, offset=offset, sort=sort)
        )
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in: dict[str, Any] | ModelType,
            session: AsyncSession,
    ):
        if not isinstance(obj_in, dict) or not isinstance(obj_in, self.model):
            msg = f'Source object should be of types: dict or {self.model}'
            self.logger.error(msg)
            raise ValueError(msg)

        db_obj = self.model(**obj_in) if isinstance(obj_in, dict) else obj_in
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            session: AsyncSession,
            attrs: dict[str, Any],
            obj_in: dict[str, Any] | ModelType,
    ):
        if not (isinstance(obj_in, dict) or isinstance(obj_in, self.model)):
            msg = f'Source object should be of types: dict or {self.model}'
            self.logger.error(msg)
            raise ValueError(msg)

        db_obj = await self.get(session, attrs)
        if db_obj is None:
            raise ValueError(f'There is no object in DB with attr={attrs}')

        if isinstance(obj_in, dict):
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
        else:
            db_obj = obj_in

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    def _make_query(
            self,
            attrs: dict[str, Any] | None = None,
            *,
            limit: int | None = None,
            offset: int | None = None,
            sort: str | None = None
    ):
        query = select(self.model)

        if attrs:
            query = select(self.model).where(
                and_(
                    *(
                        getattr(self.model, key).__eq__(value)
                        for key, value in attrs.items()
                    )
                )
            )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        if sort and self._validate_sort_query(sort):
            query = query.order_by(text(sort))

        return query  # noqa: R504

    def _validate_sort_query(self, sort: str) -> bool:
        field, direction = sort.split()
        if direction.lower() not in ['asc', 'desc']:
            self.logger.error(f'Sort query error: {sort}')
            return False

        return True
