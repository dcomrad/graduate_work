from typing import Optional, Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from src.core.config import settings
from src.core.query import (get_films_by_genre_query,
                            get_films_by_person_query, get_items_query,
                            get_sort_query)
from src.db.base import AbstractDataSource
from src.models import Film, Genre, Person
from src.services.view import ResponseView

es: Optional[AsyncElasticsearch] = None

INDEX_NAME = {
    Film: settings.elastic.movies_index,
    Genre: settings.elastic.genres_index,
    Person: settings.elastic.persons_index
}

QUERY_CREATOR = {
    'person_id': get_films_by_person_query,
    'genre_id': get_films_by_genre_query
}


class ElasticDataSource(AbstractDataSource):
    def __init__(self, model):
        super().__init__(es)
        self.model = model

    async def get_by_id(self, item_id: UUID) -> Optional[dict]:
        try:
            doc = await self.source.get(INDEX_NAME[self.model], str(item_id))
        except NotFoundError:
            return None
        return doc['_source']

    async def get_collection(
            self,
            filter: Optional[dict],
            search: Optional[dict],
            view: ResponseView
    ) -> list[dict]:
        if not filter and not search:
            body = {}
        else:
            if filter:
                body = QUERY_CREATOR[filter['field']](filter['value'])
            else:
                body = get_items_query(search['field'], search['query'])

        result = await self.source.search(
            index=INDEX_NAME[self.model],
            body=body,
            sort=get_sort_query(self.model, view.sort),
            size=view.size,
            from_=view.offset
        )
        docs = result['hits']['hits']
        return [doc['_source'] for doc in docs] if docs else []


def get_data_source(
        model: Type[Film | Genre | Person]
) -> AbstractDataSource:
    return ElasticDataSource(model)
