"""Модуль для работы с postgres."""
from typing import Iterable

from .tools.backoff import backoff
from .tools.base_postgres import BasePostgres
from .tools.logger import error, log


class PostgresManager(BasePostgres):
    """Класс для работы с postgres."""

    @staticmethod
    def generate_placeholders(placeholders_count: int):
        """Генерируем символы "?" для подстановки в запрос.
        :param placeholders_count: кол-во подставляемых данных
        """
        return ', '.join('%s' for _ in range(placeholders_count))

    @staticmethod
    def get_table_ids_query(table_name: str, updated_at: str):
        """Генерим запрос получения айдишников из таблицы
        :param table_name: таблица
        :param updated_at: начиная с какого времени updated_at собираем записи
        """
        return f"""
        SELECT id, updated_at
        FROM content.{table_name}
        WHERE updated_at > '{updated_at}'
        ORDER BY updated_at;
        """

    def query_film_work_ids(self, table_name: str, len_ids: int) -> str:
        """Генерим запрос получение из таблиц М2М
        :param table_name: название таблицы
        :param ids: список айди таблицы film_work
        """
        return f"""
        SELECT fw.id, fw.updated_at
        FROM content.film_work fw
        JOIN content.{table_name}_film_work tfw ON tfw.film_work_id = fw.id
        WHERE tfw.{table_name}_id IN ({self.generate_placeholders(len_ids)})
        ORDER BY fw.updated_at;
        """

    def query_film_works(self, film_work_len: int) -> str:
        """Генерим запрос на получение всех данных"""
        return f"""
        SELECT
        fw.id,
        fw.title,
        fw.description,
        fw.rating,
        fw.type,
        fw.created_at,
        fw.updated_at,
        COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                   'person_role', pfw.role,
                   'person_id', p.id,
                   'person_name', p.full_name
                )
            ) FILTER (WHERE p.id is not null),
            '[]'
        ) as persons,
        COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                   'id', g.id,
                   'name', g.name
                )
            ) FILTER (WHERE g.id is not null),
            '[]'
        ) as genres,
        fw.creation_date
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN ({self.generate_placeholders(film_work_len)})
        GROUP BY fw.id
        ORDER BY fw.updated_at;
        """

    def query_persons(self, persons_len):
        return f"""
        SELECT
        p.id,
        p.full_name,
        COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
               'film', pfw.film_work_id,
               'roles', ARRAY[pfw.role] || '{{}}'
            )
        ) FILTER (WHERE pfw.film_work_id is not null),
        '[]'
    ) as films
        FROM person p
        JOIN person_film_work pfw ON pfw.person_id = p.id 
        WHERE p.id IN ({self.generate_placeholders(persons_len)})
        GROUP BY p.id, pfw.film_work_id
        ORDER BY p.updated_at
        """

    def query_genres(self, genres_len):
        return f"""
        SELECT
        g.id,
        g.name,
        gfw.film_work_id
        FROM genre g
        JOIN genre_film_work gfw ON gfw.genre_id = g.id
        WHERE g.id IN ({self.generate_placeholders(genres_len)})
        ORDER BY g.updated_at
        """

    @staticmethod
    def get_entity_state(state: str, table_name: str) -> str:
        """Получаем время последних загруженных данных.
        :param state: время загруженных данных
        """
        current_state = state.get_last_state(table_name)
        if not current_state:
            return '0001-01-01 00:00:00.000000+00:00'
        else:
            return current_state

    @backoff()
    def get_ids(self, state: object, table_name: str, batch_size: int = 100) -> Iterable[list[str]]:
        """Получаем айди записей, время обновления которых выше последнего времени прохождения"""
        try:
            while True:
                last_modified = self.get_entity_state(state, table_name)
                self.execute(
                    self.get_table_ids_query(table_name, last_modified)
                )
                entity_records = self.cursor.fetchmany(batch_size)
                if not entity_records:
                    log(f'Не найдено изменений для таблицы {table_name}.')
                    break
                yield [t['id'] for t in entity_records]
                next_last_modified = entity_records[-1].get('updated_at')
                state.set_state(table_name, str(next_last_modified))
        except Exception as err:
            error(f'Ошибка при извлечении данных из {table_name}.\n{err}\n\n')
            raise err

    @backoff()
    def get_film_work_ids(self, entity_table_name: str, entity_ids: list[str], batch_size: int = 100) -> Iterable[list[str]]:
        try:
            if entity_table_name == 'film_work':
                yield entity_ids
            else:
                self.execute(
                    self.query_film_work_ids(entity_table_name, len(entity_ids)), vars=entity_ids
                )
                while True:
                    film_work_records = self.cursor.fetchmany(batch_size)
                    if not film_work_records:
                        break
                    yield [t['id'] for t in film_work_records]
        except Exception as err:
            error(f'Ошибка при извлечении данных из таблицы {entity_table_name}_film_work.\n{err}\n\n')
            raise

    @backoff()
    def get_film_works(self, film_work_ids: list[str], batch_size=100) -> Iterable[list]:
        try:
            self.execute(self.query_film_works(len(film_work_ids)), vars=film_work_ids)

            while True:
                records = self.cursor.fetchmany(batch_size)

                if not records:
                    break

                yield records
        except Exception as err:
            error(f'Ошибка при извлечении данных.\n{err}\n\n')
            raise

    @backoff()
    def get_persons(self, persons_ids: list[str], batch_size=100) -> Iterable[list]:
        try:
            self.execute(self.query_persons(len(persons_ids)), vars=persons_ids)

            while True:
                records = self.cursor.fetchmany(batch_size)

                if not records:
                    break

                yield records
        except Exception as err:
            error(f'Ошибка при извлечении данных.\n{err}\n\n')
            raise

    @backoff()
    def get_genres(self, genres_ids: list[str], batch_size=100) -> Iterable[list]:
        try:
            self.execute(self.query_genres(len(genres_ids)), vars=genres_ids)

            while True:
                records = self.cursor.fetchmany(batch_size)

                if not records:
                    break

                yield records
        except Exception as err:
            error(f'Ошибка при извлечении данных.\n{err}\n\n')
            raise
