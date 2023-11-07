from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException

from .permissions import SUPERUSER_PERMISSION


def login_required(required_permissions: list[str] | None = None):
    """Декоратор для авторизации пользователя по jwt токену. Если установлен
    параметр required_permissions, то в случае отсутствия указанного разрешения
    в списке разрешений пользователя, находящемся в jwt токене, выбрасывается
    исключение."""
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            authorize = kwargs.get('authorize')
            if authorize is None:
                msg = ('Set "authorize: AuthJWT = Depends()" as the '
                       f'"{func.__name__}" function parameter')
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=msg
                )

            await authorize.jwt_required()

            if required_permissions:
                raw_jwt = await authorize.get_raw_jwt()
                user_permissions = raw_jwt.get('permissions')
                _check_permission(user_permissions, required_permissions)

            return await func(*args, **kwargs)
        return inner
    return wrapper


def _check_permission(
        user_permissions: list[str],
        required_permissions: list[str]
) -> None:
    """Проверяет наличие требуемого разрешения, среди пользовательских."""
    allowed_permissions = {SUPERUSER_PERMISSION, *required_permissions}

    if not allowed_permissions & {*user_permissions}:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Permission denied'
        )
