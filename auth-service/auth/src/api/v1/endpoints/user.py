from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import openapi
from src.api.v1.validators import check_user_login_duplicate
from src.core.config import settings
from src.crud.users import user_crud
from src.db.postgres import get_async_session
from src.jwt import AuthJWT, login_required
from src.request_limiter import limiter
from src.schemas.access_history import AccessHistoryRead
from src.schemas.user import (UserRead, UserUpdateLogin, UserUpdatePassword,
                              UserUpdatePublicData)
from src.services.view import PaginationView, get_view_service

router = APIRouter(prefix='/me')


@router.get(
    '/',
    response_model=UserRead,
    response_model_exclude_none=True,
    response_model_exclude={'id'},
    **openapi.user.get.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def get(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    return await user_crud.get(await authorize.get_jwt_subject(), session)


@router.patch(
    '/',
    response_model=UserRead,
    response_model_exclude_none=True,
    response_model_exclude={'id'},
    **openapi.user.update.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def update(
        request: Request,  # noqa
        update_data: UserUpdatePublicData,
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    user_data = await user_crud.get(await authorize.get_jwt_subject(), session)
    return await user_crud.update(user_data, update_data, session)


@router.patch(
    '/change_login',
    response_model=UserRead,
    response_model_exclude_none=True,
    response_model_exclude={'id'},
    **openapi.user.change_login.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def change_login(
        request: Request,  # noqa
        update_data: UserUpdateLogin,
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    await check_user_login_duplicate(update_data.login, session)
    user_data = await user_crud.get(await authorize.get_jwt_subject(), session)
    return await user_crud.update(user_data, update_data, session)


@router.patch(
    '/change_password',
    response_model_exclude_none=True,
    **openapi.user.change_password.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def change_password(
        request: Request,  # noqa
        update_data: UserUpdatePassword,
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    await user_crud.update_password(await authorize.get_jwt_subject(), update_data, session)
    return True


@router.get(
    '/access_history',
    response_model=list[AccessHistoryRead],
    response_model_exclude={'id', 'user_id'},
    **openapi.user.access_history.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def access_history(
        request: Request,  # noqa
        pagination: PaginationView = Depends(get_view_service),
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    """Возвращает историю входов пользователя (ввод логина и пароля)."""
    user = await user_crud.get_with_related_fields(
        await authorize.get_jwt_subject(),
        'access_history',
        session
    )
    start, end = pagination.offset, pagination.offset + pagination.size
    return user.access_history[start:end]
