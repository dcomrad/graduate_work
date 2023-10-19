from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import raise_already_exists, raise_not_found
from src.core.utils import check_password
from src.crud import permission_crud, role_crud, user_crud
from src.db_models.user import User
from src.schemas.user import Credentials


async def check_user_login_duplicate(
        user_login: str,
        session: AsyncSession,
) -> None:
    """Проверка отсутствия в БД пользователя с логином user_login."""
    user_id = await user_crud.get_by_attribute('login', user_login, session)
    if user_id is not None:
        raise_already_exists('Пользователь с таким логином уже существует')


async def check_role_name_duplicate(
        role_name: str,
        session: AsyncSession
):
    role_id = await role_crud.get_by_attribute('name', role_name, session)
    if role_id is not None:
        raise_already_exists(f'Роль {role_name} уже существует')


async def check_permission_name_duplicate(
        permission_name: str,
        session: AsyncSession
):
    permission_id = await permission_crud.get_by_attribute('name', permission_name, session)
    if permission_id is not None:
        raise_already_exists(f'Доступ {permission_name} уже существует')


async def check_user_credentials(
        credentials: Credentials,
        session: AsyncSession
) -> User:
    """Проверяет учётные данные пользователя и в случае успеха возвращает
    объект пользователя."""
    user = await user_crud.get_by_attribute('login', credentials.login, session)

    if user is None:
        raise_not_found('Неверный логин и/или пароль')

    if not check_password(credentials.password, user.hashed_password):
        raise_not_found('Неверный логин и/или пароль')

    return user


async def assert_permission_exists(
        permission_name: str,
        session: AsyncSession
):
    permission_id = await permission_crud.get_by_attribute('name', permission_name, session)
    if permission_id is None:
        raise_already_exists(f'Доступа {permission_name} не существует')


async def assert_role_exists(
        role_name: str,
        session: AsyncSession
):
    role_id = await role_crud.get_by_attribute('name', role_name, session)
    if role_id is None:
        raise_already_exists(f'Роли {role_name} не существует')

