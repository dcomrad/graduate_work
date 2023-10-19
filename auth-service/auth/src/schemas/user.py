from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, Field, validator
from src.schemas.role import BaseRoleCreate, RoleRead


class UserRead(BaseModel):
    """Схема пользователя. Используется для http-ответа."""
    id: int
    login: str
    full_name: str
    email: str
    time_zone: str
    notifications_enabled: bool
    roles: Optional[list[RoleRead]]

    class Config:
        orm_mode = True


class UserSignup(BaseModel):
    """Схема пользователя. Используется для http-запроса."""
    login: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=3, max_length=30)
    full_name: str = Field(..., min_length=3, max_length=30)
    email: EmailStr

    @validator('*', pre=True)
    def strip_str(cls, v):
        """Метод убирает пробелы с двух сторон перед прочей валидацией."""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        extra = Extra.allow


class UserSignupExternalService(UserSignup):
    password: str = ''


class UserCreate(UserSignup):
    roles: Optional[list[BaseRoleCreate]]


class UserUpdateLogin(BaseModel):
    login: Optional[str]


class UserUpdatePassword(BaseModel):
    password: Optional[str]

    class Config:
        extra = Extra.allow


class UserUpdatePublicData(BaseModel):
    full_name: Optional[str]
    notifications_enabled: Optional[bool]
    roles: Optional[list[BaseRoleCreate]]


class Credentials(BaseModel):
    login: str
    password: str
