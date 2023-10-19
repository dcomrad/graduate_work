from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import openapi
from src.core.config import settings
from src.core.exceptions import raise_forbidden, raise_not_found
from src.crud.roles import role_crud
from src.crud.user_role import user_role_crud
from src.crud.users import user_crud
from src.db.postgres import get_async_session
from src.jwt import AuthJWT, login_required
from src.request_limiter import limiter
from src.schemas.role import RoleUpdate
from src.schemas.user import UserRead, UserUpdatePublicData
from src.schemas.user_role import UserRole

router = APIRouter(prefix='/users')


@router.get(
    '/',
    response_model=list[UserRead],
    response_model_exclude_none=True,
    **openapi.users.get_all.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='users_management')
async def get_all(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    return await user_crud.get_all(session)


@router.get(
    '/{user_id}',
    response_model=UserRead,
    response_model_exclude_none=True,
    **openapi.users.get.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='users_management')
async def get(
        request: Request,  # noqa
        user_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    user = await user_crud.get(user_id, session)
    if user is None:
        raise_not_found('Пользователь не найден')

    return user


@router.patch(
    '/{user_id}',
    response_model=UserRead,
    **openapi.users.update.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='users_management')
async def update(
        request: Request,  # noqa
        user_id: int,
        update_data: UserUpdatePublicData,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    user_data = await user_crud.get(user_id, session)
    if user_data is None:
        raise_not_found('Пользователь не найден')

    if roles := update_data.roles:
        for role in roles:
            role_data = await role_crud.get_by_attribute('name', role.name, session)
            if not role:
                raise_not_found('Роль не найдена')
            await user_role_crud.create(UserRole(user_id=user_id, role_id=role_data.id), session)
        delattr(update_data, 'roles')

    return await user_crud.update(user_data, update_data, session)

@router.delete(
    '/{user_id}/remove_user_roles',
    response_model=UserRead,
    **openapi.users.remove_user_roles.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='users_management')
async def remove_user_roles(
        request: Request,  # noqa
        user_id: int,
        roles_to_delete: list[RoleUpdate],
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    user_data = await user_crud.get(user_id, session)
    if user_data is None:
        raise_not_found('Пользователь не найден')

    if user_data.is_superuser:
        raise_forbidden('Запрещено редактирование ролей у супер-пользователя')

    role_names_to_delete = [role.name for role in roles_to_delete]
    role_ids_to_delete = [role.id for role in user_data.roles
                          if role.name in role_names_to_delete]
    user_roles_m2m = [user_role for user_role in user_data._roles]

    for role in user_roles_m2m:
        if role.role_id in role_ids_to_delete:
            await user_role_crud.delete(role, session)

    await session.refresh(await user_crud.get(user_id, session))
    return await user_crud.get(user_id, session)
