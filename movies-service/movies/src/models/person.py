from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.models.mixins import JSONMixin


class FilmRole(BaseModel):
    """Модель информации о фильме со списком ролей в нём."""
    film: UUID = Field(..., title='ID фильма')
    roles: list[str] = Field(..., title='Список ролей')

    class Config(JSONMixin):
        title = 'Фильм и список ролей в нём'


class Person(BaseModel, JSONMixin):
    """Модель информации о персоне."""
    uuid: UUID = Field(..., alias='id', title='ID человека')
    full_name: str = Field(..., title='Полное имя человека')
    films: Optional[list[FilmRole]] = Field(None,
                                            title='Список фильмов и ролей')

    class Config(JSONMixin):
        title = 'Подробная информация о человеке'
