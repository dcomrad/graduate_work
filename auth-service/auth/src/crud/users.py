from logging import info
from random import randrange

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.utils import hash_password
from src.crud.base import CRUDBase
from src.db_models.user import User
from src.schemas.user import UserSignupExternalService


class CRUDUsers(CRUDBase):
    """Класс для выполнение CRUD операция над моделью User."""
    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        info(f'Вызов метода create для {self.model}.'
             f'Параметры вызова: '
             f' obj_in: {obj_in.dict()}')
        """Создаёт пользователя, предварительно подменяя введённый им пароль на
        его специально сформированный хеш."""
        if hasattr(obj_in, 'password'):
            setattr(
                obj_in,
                'hashed_password',
                hash_password(obj_in.password) if obj_in.password else obj_in.password
            )
            delattr(obj_in, 'password')
        return await super().create(obj_in, session)

    async def create_with_unique_login(
            self,
            user: UserSignupExternalService,
            session: AsyncSession,
    ):
        """Пытается рекурсивно создать пользователя в """
        for _ in range(20):
            try:
                return await self.create(user, session)
            except Exception:
                # TODO: разрешить проблему многократного использования сессии
                user.login = f'{user.login}{randrange(1, 9)}'
        raise ValueError('Cannot create user')

    async def update_password(
            self,
            user_id,
            obj_in,
            session: AsyncSession
    ):
        info(f'Вызов метода update_password для {self.model}.'
             f'Параметры вызова: '
             f' user_id: {user_id}'
             f' obj_in: {obj_in.dict()}')
        setattr(obj_in, 'hashed_password', hash_password(obj_in.password))
        delattr(obj_in, 'password')
        return await super().update_by_attribute('id', user_id, obj_in, session)


user_crud = CRUDUsers(User)
