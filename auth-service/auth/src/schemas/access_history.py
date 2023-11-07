from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccessHistoryBase(BaseModel):
    """Базовая схема истории входов пользователя."""
    user_id: UUID
    user_agent: str


class AccessHistoryRead(AccessHistoryBase):
    """Схема истории входов пользователя. Используется для http ответа."""
    id: UUID
    access_time: datetime

    class Config:
        orm_mode = True


class AccessHistoryCreate(AccessHistoryBase):
    """Схема истории входов пользователя. Используется при создании объекта
    модели."""
    pass
