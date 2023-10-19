from http import HTTPStatus

from async_fastapi_jwt_auth.exceptions import RevokedTokenError
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import openapi
from src.api.v1.validators import (check_user_credentials,
                                   check_user_login_duplicate)
from src.core.config import settings
from src.core.exceptions import raise_already_exists
from src.core.tokens import Token, get_user_tokens
from src.core.utils import get_user_agent
from src.crud import access_history_crud, user_crud, user_service_crud
from src.db.postgres import get_async_session
from src.db.redis import RedisTokenStorage, get_token_storage
from src.jwt import AuthJWT, login_required
from src.request_limiter import limiter
from src.schemas.access_history import AccessHistoryCreate
from src.schemas.oauth import UserServiceCreate
from src.schemas.user import (Credentials, UserRead, UserSignup,
                              UserSignupExternalService)
from src.services.oauth import OAuthBase, get_oauth_service

router = APIRouter(prefix='/auth')


@router.post(
    '/signup',
    response_model=UserRead,
    **openapi.auth.signup.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
async def signup(
        request: Request,  # noqa
        user: UserSignup,
        session: AsyncSession = Depends(get_async_session)
):
    """Регистрирует пользователя."""
    await check_user_login_duplicate(user.login, session)
    return await user_crud.create(user, session)


@router.post(
    '/login',
    response_model=Token,
    **openapi.auth.login.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
async def login(
        request: Request,  # noqa
        credentials: Credentials,
        authorize: AuthJWT = Depends(),
        user_agent: str = Depends(get_user_agent),
        token_storage: RedisTokenStorage = Depends(get_token_storage),
        session: AsyncSession = Depends(get_async_session)
):
    """Авторизует пользователя и выдает access и refresh токены."""
    user = await check_user_credentials(credentials, session)

    await access_history_crud.create(
        AccessHistoryCreate(user_id=user.id, user_agent=user_agent),
        session
    )

    return await get_user_tokens(user, user_agent, authorize, token_storage)


@router.post(
    '/logout',
    **openapi.auth.logout.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def logout(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),
        user_agent: str = Depends(get_user_agent),
        token_storage: RedisTokenStorage = Depends(get_token_storage),
):
    """Аннулирует выданный ранее refresh токен."""
    await token_storage.delete_token(user=await authorize.get_jwt_subject(),
                                     user_agent=user_agent)

    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.post(
    '/logout_others',
    **openapi.auth.logout_others.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def logout_others(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),
        user_agent: str = Depends(get_user_agent),
        token_storage: RedisTokenStorage = Depends(get_token_storage),
):
    """Аннулирует выданные ранее refresh токены, за исключением того, который
    "привязан" к текущему устройству пользователя."""
    await token_storage.delete_tokens(user=await authorize.get_jwt_subject(),
                                      exclude_user_agent=user_agent)

    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.post(
    '/refresh',
    response_model=Token,
    **openapi.auth.refresh.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
async def refresh(
        request: Request,  # noqa
        user_agent: str = Depends(get_user_agent),
        authorize: AuthJWT = Depends(),
        token_storage: RedisTokenStorage = Depends(get_token_storage),
        session: AsyncSession = Depends(get_async_session)
):
    """Обновляет пару access и refresh токенов."""
    await authorize.jwt_refresh_token_required()
    user_id = await authorize.get_jwt_subject()

    token = await token_storage.get_token(user_id, user_agent)
    if token != await authorize.get_jti(authorize._token):
        raise RevokedTokenError(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                message='Invalid refresh token')

    user = await user_crud.get(user_id, session)

    return await get_user_tokens(user, user_agent, authorize, token_storage)


@router.post(
    '/login_with_external_account',
    **openapi.auth.login_with_external_account.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
async def login_with_external_account(
        request: Request,  # noqa
        code: str = Query(None, description='Код подтверждения, полученный от OAuth сервиса'),
        service: OAuthBase = Depends(get_oauth_service),
        authorize: AuthJWT = Depends(),
        user_agent: str = Depends(get_user_agent),
        token_storage: RedisTokenStorage = Depends(get_token_storage),
        session: AsyncSession = Depends(get_async_session)
):
    if not code:
        url = await service.get_auth_url()
        return {'auth_url': url}

    client = await service.get_client(code, session)

    if not client.service['is_linked']:
        #  если ранее пользователь из такого сервиса не осуществлял вход, ищем
        #  пользователя по email
        user = await user_crud.get_by_attribute('email', client.email, session)

        if user is None:
            user = await user_crud.create_with_unique_login(
                UserSignupExternalService(
                    login=client.login,
                    full_name=client.full_name,
                    email=client.email
                ),
                session
            )

        await user_service_crud.create(
            UserServiceCreate(user_id=user.id, service_id=client.service['id'],
                              user_service_id=client.id),
            session
        )
    else:
        user = await user_crud.get(client.service['user_id'], session)

    await access_history_crud.create(
        AccessHistoryCreate(user_id=user.id, user_agent=user_agent),
        session
    )

    return await get_user_tokens(user, user_agent, authorize, token_storage)


@router.post(
    '/link_external_account',
    **openapi.auth.link_external_account.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required()
async def link_external_account(
        request: Request,  # noqa
        code: str = Query(None, description='Код подтверждения, полученный от OAuth сервиса'),
        service: OAuthBase = Depends(get_oauth_service),
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    if not code:
        url = await service.get_auth_url()
        return {'auth_url': url}

    client = await service.get_client(code, session)

    if client.service['is_linked']:
        raise_already_exists(
            f'Связь с {client.service["name"]} ({client.login}) уже установлена'
        )

    user_id = await authorize.get_jwt_subject()
    await user_service_crud.create(
        UserServiceCreate(user_id=user_id, service_id=client.service['id'],
                          user_service_id=client.id),
        session
    )

    return Response(
        f'Привязка к аккаунту {client.service["name"]} ({client.login}) успешно выполнена',
        status_code=HTTPStatus.OK
    )
