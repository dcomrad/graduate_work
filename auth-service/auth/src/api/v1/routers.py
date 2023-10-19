from fastapi import APIRouter
from src.api.v1.endpoints import (auth_router, permissions_router,
                                  roles_router, user_router, users_router)

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(auth_router, tags=['Auth'])
v1_router.include_router(user_router, tags=['User'])
v1_router.include_router(users_router, tags=['Users'])
v1_router.include_router(roles_router, tags=['Roles'])
v1_router.include_router(permissions_router, tags=['Permissions'])
