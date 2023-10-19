from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.models.mixins import JSONMixin


class Genre(BaseModel):
    """Модель информации о жанре."""
    id: UUID = Field(..., title='ID жанра')
    name: str = Field(..., title='Название жанра')
    description: Optional[str] = Field(None, title='Описание жанра')

    class Config(JSONMixin):
        title = 'Подробная информация о жанре'
