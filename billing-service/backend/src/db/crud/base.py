import logging
from typing import Any, Sequence

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = Any


class CRUDBase:
    def __init__(self, model: ModelType, logger: logging.Logger):
        self.model = model
        self.logger = logger

    async def get(
            self,
            session: AsyncSession,
            attrs: dict[str, Any]
    ) -> ModelType | None:
        """Возвращает первый элемент, соответствующий условию поиска в attrs.
        Например:
            attrs={'id': 5} - вернёт запись, у которого id=5
        Обычно используется, есть уверенность, что в БД есть только один
        элемент, соответствующий условию.
        """
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
    ) -> Sequence[ModelType]:
        """Возвращает список элементов, удовлетворяющих условию поиска в attrs.
        Например:
            attrs={'is_active': True} - вернёт все активные записи
        :param sort: ключ сортировки (<имя поля> asc | desc)
        """
        db_objs = await session.execute(
            self._make_query(attrs, limit=limit, offset=offset, sort=sort)
        )
        return db_objs.scalars().all()

    async def create(
            self,
            session: AsyncSession,
            obj_in: dict[str, Any] | ModelType,
    ) -> ModelType:
        """Создаёт в БД запись из полученного объекта. Может быть передан как
        словарь с данными, необходимыми для создания объекта модели, там и сам
        объект модели."""
        if not (isinstance(obj_in, dict) or isinstance(obj_in, self.model)):
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
            obj_in: dict[str, Any],
    ) -> Sequence[ModelType]:
        """Обновляет все записи в БД, соответствующие условию поиска в
        attrs. Словарь obj_in содержит обновляемые поля и их значения."""
        if not isinstance(obj_in, dict):
            msg = 'Source object should be of type dict'
            self.logger.error(msg)
            raise ValueError(msg)

        db_objs = await self.get_all(session, attrs)

        for db_obj in db_objs:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            session.add(db_obj)

        await session.commit()
        return db_objs

    async def delete(
            self,
            session: AsyncSession,
            attrs: dict[str, Any]
    ) -> Sequence[ModelType]:
        """Удаляет элементы, соответствующие условию поиска в attrs."""
        db_objs = await self.get_all(session, attrs)

        for db_obj in db_objs:
            await session.delete(db_obj)

        await session.commit()
        return db_objs

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
