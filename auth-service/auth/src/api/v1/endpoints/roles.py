from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import openapi
from src.api.v1.validators import (assert_permission_exists,
                                   check_role_name_duplicate)
from src.core.config import settings
from src.core.exceptions import raise_not_found
from src.crud.permissions import permission_crud
from src.crud.role_permission import role_permission_crud
from src.crud.roles import role_crud
from src.db.postgres import get_async_session
from src.jwt import AuthJWT, login_required
from src.request_limiter import limiter
from src.schemas.permission import PermissionRead, PermissionUpdate
from src.schemas.role import (ExtendedRoleCreate, ExtendedRoleRead, RoleRead,
                              RoleUpdate)
from src.schemas.role_permission import RolePermissionCreate

router = APIRouter(prefix='/roles')


@router.get(
    '/',
    response_model=list[ExtendedRoleRead],
    response_model_exclude_none=True,
    **openapi.roles.get_all.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def get_all(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    return await role_crud.get_all(session)


@router.get(
    '/{role_id}',
    response_model=RoleRead,
    response_model_exclude_none=True,
    **openapi.roles.get.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def get(
        request: Request,  # noqa
        role_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    role = await role_crud.get(role_id, session)
    if role is None:
        raise_not_found('Роль не найдена')

    return role


@router.get(
    '/{role_id}/get_role_permissions',
    response_model=list[PermissionRead],
    response_model_exclude_none=True,
    **openapi.roles.get_role_permissions.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def get_role_permissions(
        request: Request,  # noqa
        role_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    result = await role_crud.get_by_attribute('id', role_id, session)
    return result.permissions


@router.post(
    '/',
    response_model=RoleRead,
    response_model_exclude_none=True,
    **openapi.roles.create.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def create(
        request: Request,  # noqa
        role: ExtendedRoleCreate,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    await check_role_name_duplicate(role.name, session)

    permissions = role.permissions
    delattr(role, 'permissions')

    if permissions:
        for permission in permissions:
            await assert_permission_exists(permission.name, session)

    new_role = await role_crud.create(role, session)

    if permissions:
        # Дважды проходим по списку пермишенов, потому что:
        # 1) Роль добавляем перед добавлением пермишенов.
        # 2) Перед добавлением роли нужно убедиться, что переданный список пермишенов существует,
        # иначе получится так что может добавиться роль с неполным списком пермишенов
        for permission in permissions:
            permission = await permission_crud.get_by_attribute('name', permission.name, session)
            await role_permission_crud.create(RolePermissionCreate(role_id=new_role.id, permission_id=permission.id), session)

    return new_role


@router.patch(
    '/{role_id}',
    response_model=RoleRead,
    response_model_exclude_none=True,
    **openapi.roles.update.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def update(
        request: Request,  # noqa
        role_id: int,
        role_update_data: RoleUpdate,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    role_data = await role_crud.get(role_id, session)
    await check_role_name_duplicate(role_update_data.name, session)
    return await role_crud.update(role_data, role_update_data, session)


@router.delete(
    '/{role_id}',
    **openapi.roles.delete.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def delete(
        request: Request,  # noqa
        role_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    role_data = await role_crud.get(role_id, session)
    await role_crud.delete(role_data, session)
    return True


@router.delete(
    '/{role_id}/remove_role_permissions',
    response_model=ExtendedRoleRead,
    **openapi.roles.remove_role_permissions.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def remove_role_permissions(
        request: Request,  # noqa
        role_id: int,
        permissions_to_delete: list[PermissionUpdate],
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    role_data = await role_crud.get(role_id, session)
    if role_data is None:
        raise_not_found('Роль не найдена')

    permission_names_to_delete = [permission.name for permission in permissions_to_delete]
    permission_ids_to_delete = [permission.id for permission in role_data.permissions
                                if permission.name in permission_names_to_delete]
    role_permissions_m2m = [role_permission for role_permission in role_data._permissions]

    for permission in role_permissions_m2m:
        if permission.permission_id in permission_ids_to_delete:
            await role_permission_crud.delete(permission, session)

    await session.refresh(await role_crud.get(role_id, session))
    return await role_crud.get(role_id, session)
