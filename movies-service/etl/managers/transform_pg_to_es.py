from typing import Callable, Optional

from .tools.logger import error


def transform_film_work_to_es(es_index_name, pg_data: list) -> list[dict]:
    """Преобразуем данные из постгрес film_work в формат для es"""
    prepared_data = []

    def is_actor(person: dict) -> bool:
        return person.get('person_role') == 'actor'

    def is_writer(person: dict) -> bool:
        return person.get('person_role') == 'writer'

    def is_director(person: dict) -> bool:
        return person.get('person_role') == 'director'

    def get_names(persons: list[dict]) -> list[Optional[str]]:
        def get_name(person: dict) -> Optional[str]:
            return person.get('full_name')

        return list(map(get_name, persons))

    def get_persons(persons: list[dict], pred: Callable) -> list[dict]:
        def strip_fields(p: dict) -> dict:
            return {'id': p.get('person_id'),
                    'full_name': p.get('person_name')}

        return list(map(strip_fields, filter(pred, persons)))

    try:
        for row in pg_data:
            persons = row.get('persons')
            actors = get_persons(persons, is_actor)
            writers = get_persons(persons, is_writer)
            directors = get_persons(persons, is_director)
            prepared_row = {
                'id': row.get('id'),
                'imdb_rating': row.get('rating'),
                'genres': row.get('genres'),
                'title': row.get('title'),
                'description': row.get('description'),
                'actors_names': get_names(actors),
                'writers_names': get_names(writers),
                'directors_names': get_names(directors),
                'actors': actors,
                'writers': writers,
                'directors': directors,
                'creation_date': row.get('creation_date')
            }
            row_index = {
                'index': {
                    '_index': es_index_name,
                    '_id': row.get('id')
                }
            }
            prepared_data.append(row_index)
            prepared_data.append(prepared_row)
    except Exception as err:
        error(
            f'Ошибка во время преобразования данных.\n{err}\n\n')
        raise err

    return prepared_data


def transform_person_to_es(es_index_name, pg_data: list) -> list[dict]:
    """Преобразуем данные из постгрес person в формат для es"""
    prepared_data = []

    try:
        for row in pg_data:
            prepared_row = {
                'id': row.get('id'),
                'full_name': row.get('full_name'),
                'films': row.get('films')
            }
            row_index = {
                'index': {
                    '_index': es_index_name,
                    '_id': row.get('id')
                }
            }
            prepared_data.append(row_index)
            prepared_data.append(prepared_row)
    except Exception as err:
        error(
            f'Ошибка во время преобразования данных.\n{err}\n\n')
        raise err

    return prepared_data


def transform_genre_to_es(es_index_name, pg_data: list) -> list[dict]:
    """Преобразуем данные из постгрес person в формат для es"""
    prepared_data = []

    try:
        for row in pg_data:
            prepared_row = {
                'id': row.get('id'),
                'name': row.get('name'),
                'description': row.get('description')
            }
            row_index = {
                'index': {
                    '_index': es_index_name,
                    '_id': row.get('id')
                }
            }
            prepared_data.append(row_index)
            prepared_data.append(prepared_row)
    except Exception as err:
        error(
            f'Ошибка во время преобразования данных.\n{err}\n\n')
        raise err

    return prepared_data
