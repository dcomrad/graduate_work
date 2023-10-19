from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import openapi
from src.api.v1.validators import check_permission_name_duplicate
from src.core.config import settings
from src.core.exceptions import raise_not_found
from src.crud.permissions import permission_crud
from src.db.postgres import get_async_session
from src.jwt import AuthJWT, login_required
from src.request_limiter import limiter
from src.schemas.permission import (PermissionCreate, PermissionRead,
                                    PermissionUpdate)

router = APIRouter(prefix='/permissions')


@router.get(
    '/',
    response_model=list[PermissionRead],
    response_model_exclude_none=True,
    **openapi.permissions.get_all.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def get_all(
        request: Request,  # noqa
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    return await permission_crud.get_all(session)


@router.get(
    '/{permission_id}',
    response_model=PermissionRead,
    response_model_exclude_none=True,
    **openapi.permissions.get.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def get(
        request: Request,  # noqa
        permission_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    permission = await permission_crud.get(permission_id, session)
    if permission is None:
        raise_not_found('Такое разрешение не найдено')

    return permission


@router.post(
    '/',
    response_model=PermissionRead,
    response_model_exclude_none=True,
    **openapi.permissions.create.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def create(
        request: Request,  # noqa
        permission: PermissionCreate,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    await check_permission_name_duplicate(permission.name, session)
    return await permission_crud.create(permission, session)


@router.patch(
    '/{permission_id}',
    response_model=PermissionRead,
    response_model_exclude_none=True,
    **openapi.permissions.update.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def update(
        request: Request,  # noqa
        permission_id: int,
        permission_update_data: PermissionUpdate,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    permission_data = await permission_crud.get(permission_id, session)
    if permission_data.name:
        await check_permission_name_duplicate(permission_update_data.name, session)
    return await permission_crud.update(permission_data, permission_update_data, session)


@router.delete(
    '/{permission_id}',
    **openapi.permissions.delete.dict()
)
@limiter.limit(f"{settings.project.rpm_limit}/minute")
@login_required(required_permission='access_management')
async def delete(
        request: Request,  # noqa
        permission_id: int,
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session)
):
    permission_data = await permission_crud.get(permission_id, session)
    await permission_crud.delete(permission_data, session)
    return True
