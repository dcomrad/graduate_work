from functools import lru_cache
from typing import Optional, Type
from uuid import UUID

from src.db.base import AbstractDataSource
from src.db.elastic import get_data_source
# from src.db.redis import cache
from src.models import Film, Genre, Person


class DetailService:
    """Класс, отвечающий за получение одного элемента из хранилища."""
    def __init__(self,
                 model: Type[Film | Genre | Person],
                 data_source: AbstractDataSource):
        self.model = model
        self.data_source = data_source

    # @cache._from_cache
    async def get_by_id(
            self,
            item_id: UUID
    ) -> Optional[Film | Genre | Person]:
        """Возвращает из хранилища элемент по его id.
        :param item_id: id искомого элемента
        """
        item = await self.data_source.get_by_id(item_id)
        return None if item is None else self.model(**item)


def get_detail_service(
        model: Type[Film | Genre | Person],
        data_source: AbstractDataSource
) -> DetailService:
    return DetailService(model, data_source)


@lru_cache()
def get_film_detail_service() -> DetailService:
    return get_detail_service(Film, get_data_source(Film))


@lru_cache()
def get_genre_detail_service() -> DetailService:
    return get_detail_service(Genre, get_data_source(Genre))


@lru_cache()
def get_person_detail_service() -> DetailService:
    return get_detail_service(Person, get_data_source(Person))
