from time import sleep

from managers.data.elastic_schemas import *
from managers.elastic_manager import ElasticManager
from managers.postgres_manager import PostgresManager
from managers.redis_storage_manager import RedisStorage, State
from managers.tools.backoff import backoff
from managers.tools.config import es_data, pg_data, redis_data
from managers.tools.logger import error, log
from managers.transform_pg_to_es import (transform_film_work_to_es,
                                         transform_genre_to_es,
                                         transform_person_to_es)

connections = {
    'pg_client': None,
    'es_client': None,
    'redis': None
}


def check_connection(pg_client, es_client, redis_client):
    """Проверяем соединения с бд"""
    return all((pg_client.alive(), es_client.alive(), redis_client.alive()))


def run(table_name: str, pg_client, es_client, redis_client) -> None:
    """Общая логика работы переноса данных."""

    try:
        for entity_ids in pg_client.get_ids(redis_client, table_name):
            for film_work_ids in pg_client.get_film_work_ids(table_name, entity_ids):
                if not film_work_ids:
                    return
                for film_works in pg_client.get_film_works(film_work_ids):
                    es_data = transform_film_work_to_es(
                        es_client.get_index_name_by_table_name('film_work'),
                        film_works
                    )
                    es_client.save_data('film_work', es_data)
            if table_name == 'person':
                for persons in pg_client.get_persons(entity_ids):
                    es_data = transform_person_to_es(
                        es_client.get_index_name_by_table_name('person'),
                        persons
                    )
                    es_client.save_data('person', es_data)
            if table_name == 'genre':
                for genres in pg_client.get_genres(entity_ids):
                    es_data = transform_genre_to_es(
                        es_client.get_index_name_by_table_name('genre'),
                        genres
                    )
                    es_client.save_data('genre', es_data)

    except Exception as pipeline_err:
        error(f'Failed while running the pipeline.\n{pipeline_err}\n\n')


@backoff()
def main() -> None:
    """Функция перебора таблиц и вызова обработки для каждой"""
    with PostgresManager(**pg_data) as pg_client, \
         ElasticManager(**es_data) as es_client, \
         State(RedisStorage(**redis_data).connect()) as state_client:

        for index in es_client.indexes.items():
            es_client.create_index(index[1], schemas[index[0]])

        while True:
            if not check_connection(pg_client, es_client, state_client):
                #  Рейзим чтобы выбросило в бэкофф и произошло переподключение в with
                raise RuntimeError('Одно из подключений оставило нас :( ')

            for table_name in ('film_work', 'genre', 'person'):
                log(f'Экспортируем {table_name}')
                run(table_name, pg_client, es_client, state_client)

            sleep(10)


if __name__ == '__main__':
    main()
