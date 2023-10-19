from pydantic import BaseModel


class PermissionBase(BaseModel):
    description: str | None


class PermissionRead(PermissionBase):
    id: int
    name: str

    class Config:
        orm_mode = True


class PermissionCreate(PermissionBase):
    name: str


class PermissionUpdate(PermissionBase):
    name: str | None
