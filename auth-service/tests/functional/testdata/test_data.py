from typing import Optional

from pydantic import BaseModel


class Permission(BaseModel):
    id: int = None
    name: str = None
    description: str = None


class Role(BaseModel):
    id: int = None
    name: str = None
    description: str = None
    permissions: list[Permission] = None


class User(BaseModel):
    id: int = None
    full_name: str = None
    login: str = None
    password: str = None
    roles: Optional[list[Role]] = None


class UserRole(BaseModel):
    user_id: int
    role_id: int


class RolePermission(BaseModel):
    role_id: int
    permission_id: int


class UserWithAccessPermissions(BaseModel):
    id: int = 10001
    login: str = 'test_user_1'
    password: str = 'password123'
    is_superuser: bool = False
    full_name: str = 'test user with permissions'
