from functools import lru_cache
from typing import Optional, Type

from src.db.base import AbstractDataSource
from src.db.elastic import get_data_source
# from src.db.redis import cache
from src.models import Film, Genre, Person
from src.services.view import ResponseView


class CollectionService:
    """Класс, отвечающий за получение коллекции элементов из источника
    данных."""
    def __init__(self,
                 model: Type[Film | Genre | Person],
                 data_source: AbstractDataSource):
        self.model = model
        self.data_source = data_source

    # @cache._from_cache
    async def get_collection(
            self,
            filter: Optional[dict],
            search: Optional[dict],
            view: ResponseView
    ) -> list[Film | Genre | Person]:
        """Возвращает коллекцию документов, найденных по запросу.
        :param filter: id для фильтрации
        :param search: поисковый запрос
        :param view: сервис, отвечающий за представления элементов коллекции
        (сортировка, пагинация)
        """
        items = await self.data_source.get_collection(
            filter=filter, search=search, view=view
        )
        return [self.model(**item) for item in items] if items else []


def get_collection_service(
        model: Type[Film | Genre | Person],
        data_source: AbstractDataSource
) -> CollectionService:
    return CollectionService(model, data_source)


@lru_cache()
def get_film_collection_service() -> CollectionService:
    return get_collection_service(Film, get_data_source(Film))


@lru_cache()
def get_genre_collection_service() -> CollectionService:
    return get_collection_service(Genre, get_data_source(Genre))


@lru_cache()
def get_person_collection_service() -> CollectionService:
    return get_collection_service(Person, get_data_source(Person))
