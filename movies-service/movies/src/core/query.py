from typing import Optional, Type
from uuid import UUID

from src.core.utils import raise_402
from src.models import Film, Genre, Person

ALLOWED_SORT_FIELDS = {
    Film: ['imdb_rating'],
    Genre: ['name'],
    Person: ['full_name']
}


def get_sort_query(model: Type[Film | Genre | Person],
                   sort: Optional[str] = None) -> Optional[str]:
    """Формирует строку с параметрами сортировки для elasticsearch.
    :param model: модель, в которую конвертируется результат поиска
    :param sort: запрос на сортировку, полученный от пользователя
    """
    if sort is None:
        return None

    direction = 'desc' if sort[0] == '-' else 'asc'
    field = sort[1:] if sort[0] in ['-', '+'] else sort
    if field not in ALLOWED_SORT_FIELDS[model]:
        message = (f'Сортировка по полю "{field}" невозможна. '
                   f'Доступные поля: {ALLOWED_SORT_FIELDS[model]}')
        raise_402(message)

    return f'{field}:{direction}'


def get_items_query(field: str, query: str) -> dict:
    """Формирует поисковый запрос на фильтрацию документов elasticsearch.
    :param field: поле, по которому ведётся поиск
    :param query: поисковый запрос
    """
    return {
        'query': {
            'match': {
                field: query
            }
        },
    }


def get_films_by_genre_query(
        genre_id: Optional[UUID | list[UUID]] = None) -> Optional[dict]:
    """Формирует поисковый запрос на фильтрацию фильмов заданного жанра."""
    if genre_id is None:
        return None

    genre_id = genre_id if isinstance(genre_id, list) else [genre_id]

    match_query = [{'match': {'genres.id': _id}} for _id in genre_id]

    return {
        'query': {
            'nested': {
                'path': 'genres',
                'query': {
                    'bool': {
                        'should': [
                            *match_query
                        ]
                    }
                }
            }
        },
    }


def get_films_by_person_query(person_id: UUID) -> Optional[dict]:
    """Формирует поисковый запрос на фильтрацию фильмов по имени лица,
    участвующего в производстве."""
    fields = ['actors', 'writers', 'directors']

    match_query = [
        {
            'nested': {
                'path': field,
                'query': {
                    'match': {
                        f'{field}.id': person_id
                    }
                }
            }
        } for field in fields
    ]

    return {
        'query': {
            'bool': {
                'should': [
                    *match_query
                ]
            }
        }
    }
