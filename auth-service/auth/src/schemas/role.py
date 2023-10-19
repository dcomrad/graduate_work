from typing import Optional

from pydantic import BaseModel
from src.schemas.permission import PermissionCreate, PermissionRead


class RoleBase(BaseModel):
    description: str | None


class RoleRead(RoleBase):
    id: int
    name: str

    class Config:
        orm_mode = True


class ExtendedRoleRead(RoleBase):
    id: int
    name: str
    permissions: Optional[list[PermissionRead]]

    class Config:
        orm_mode = True


class BaseRoleCreate(RoleBase):
    name: str


class ExtendedRoleCreate(BaseRoleCreate):
    permissions: Optional[list[PermissionCreate]]


class RoleUpdate(RoleBase):
    name: str | None
