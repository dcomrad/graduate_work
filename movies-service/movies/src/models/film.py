from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.models.genre import Genre
from src.models.mixins import JSONMixin
from src.models.person import Person


class FilmBase(BaseModel):
    uuid: UUID = Field(..., alias='id', title='ID фильма')
    title: str = Field(..., title='Название фильма')
    imdb_rating: float = Field(..., title='Рейтинг фильма')


class Film(FilmBase):
    """Модель полной информации о фильме."""
    description: Optional[str] = Field(None, title='Описание фильма')
    genres: Optional[list[Genre]] = Field(None, title='Список жанров')
    actors: Optional[list[Person]] = Field(None, title='Список актёров')
    writers: Optional[list[Person]] = Field(None, title='Список сценаристов')
    directors: Optional[list[Person]] = Field(None, title='Список режиссёров')

    class Config(JSONMixin):
        title = 'Подробная информация о фильме'


class FilmShortView(FilmBase):
    """Модель сокращённой информации о фильме."""
    class Config(JSONMixin):
        title = 'Краткая информация о фильме'
