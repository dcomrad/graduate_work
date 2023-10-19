from logging import info
from typing import Any, Callable

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CRUDBase:
    """Базовый класс для выполнение основных CRUD операция над переданной в
    конструктор моделью."""
    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        """Метод получения объекта модели по id."""
        info(f'Вызов метода get для {self.model}.\n'
             f'Параметры вызова:\n'
             f' id: {obj_id}\n')
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_with_related_fields(
            self,
            obj_id: int,
            related_fields: str | list[str],
            session: AsyncSession,
    ):
        """Метод получения объекта модели по id. Применяется, когда у модели
        есть поля со стратегией загрузки 'select' (lazyload), к которым нужно
        обратиться после получения объекта модели. В противном случае, при
        обращении будет выброшено исключение, т.к. в асинхронном режиме сессия
        уже будет недоступна.
        :param obj_id - id записи
        :param related_fields - значение или список значений полей, которые
        нужно загрузить в рамках одной сессии."""
        info(f'Вызов метода get_with_related_fields для {self.model}.\n'
             f'Параметры вызова:\n'
             f' id: {obj_id}\n'
             f' related_fields: {related_fields}\n')
        if not isinstance(related_fields, list):
            related_fields = [related_fields]

        loaders = [
            selectinload(getattr(self.model, related_field))
            for related_field in related_fields
        ]

        db_obj = await session.execute(
            select(self.model).options(*loaders).where(self.model.id == obj_id)
        )

        return db_obj.scalars().first()

    async def get_by_attribute(
            self,
            attr_names: Any | list[Any],
            attr_values: Any | list[Any],
            session: AsyncSession,
    ):
        if isinstance(attr_names, list):
            if not isinstance(attr_values, list):
                raise ValueError('attr_names and attr_values both must be single values or lists')
            if len(attr_names) != len(attr_values):
                raise ValueError('attr_names and attr_values must be the same length')
        else:
            attr_names, attr_values = [attr_names], [attr_values]

        db_obj = await session.execute(
            select(self.model).where(
                self._make_query_chain(attr_names, attr_values, and_)
            )
        )
        return db_obj.scalars().first()

    async def get_all_by_attribute(
            self,
            attr_name: Any,
            attr_value: Any,
            session: AsyncSession,
    ):
        info(f'Вызов метода get_all_by_attribute для {self.model}.\n'
             f'Параметры вызова:\n'
             f' attr_name: {attr_name}\n'
             f' attr_value: {attr_value}\n')
        db_obj = await session.execute(
            select(self.model).where(
                getattr(self.model, attr_name) == attr_value
            )
        )
        return db_obj.unique().scalars().all()

    async def get_all(
            self,
            session: AsyncSession
    ):
        info(f'Вызов метода get_all для {self.model}.\n'
             f'Параметры вызова: <>\n')
        """Получение всех объектов модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.unique().scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        info(f'Вызов метода create для {self.model}.\n'
             f'Параметры вызова:\n'
             f' obj_in: {obj_in.dict()}\n')
        """Создание в БД записи, соответствующей объекту модели, наполненного
        данными из аргумента obj_in."""
        db_obj = self.model(**obj_in.dict())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        """Обновление записи в БД, соответствующей объекту модели, поля
        которого обновлены в соответствии с аргументом obj_in."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        info(f'Вызов метода update для {self.model}.\n'
             f'Параметры вызова:\n'
             f' db_obj: {obj_data}\n'
             f' obj_in: {update_data}\n')

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_by_attribute(
            self,
            attr_name,
            attr_value,
            update_data,
            session: AsyncSession
    ):
        info(f'Вызов метода update_by_attribute для {self.model}.\n'
             f'Параметры вызова:\n'
             f' attr_name: {attr_name}\n'
             f' attr_value: {attr_value}\n'
             f' update_data: {update_data.dict(exclude_unset=True)}\n')
        data = await self.get_by_attribute(attr_name, attr_value, session)
        return await self.update(data, update_data, session)

    async def delete(
            self,
            db_obj,
            session: AsyncSession,
    ):
        info(f'Вызов метода delete для {self.model}.\n'
             f'Параметры вызова:\n'
             f' db_obj: {jsonable_encoder(db_obj)}\n')
        """Метод удаления записи в БД, соответствующего объекту модели db_obj."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    def _make_query_chain(
            self,
            names: list[Any],
            values: list[Any],
            operator: Callable
    ):
        if len(names) == 1:
            return getattr(self.model, names[0]).__eq__(values[0])

        return operator(
            getattr(self.model, names[0]).__eq__(values[0]),
            self._make_query_chain(names[1:], values[1:], operator)
        )
