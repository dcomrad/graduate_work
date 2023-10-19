from datetime import datetime

from pydantic import BaseModel


class AccessHistoryBase(BaseModel):
    """Базовая схема истории входов пользователя."""
    user_id: int
    user_agent: str


class AccessHistoryRead(AccessHistoryBase):
    """Схема истории входов пользователя. Используется для http ответа."""
    id: int
    access_time: datetime

    class Config:
        orm_mode = True


class AccessHistoryCreate(AccessHistoryBase):
    """Схема истории входов пользователя. Используется при создании объекта
    модели."""
    pass
