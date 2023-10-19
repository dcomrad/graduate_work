import psycopg2
from psycopg2 import extras
from psycopg2.errors import InFailedSqlTransaction

from .backoff import backoff
from .logger import log


class BasePostgres:
    """Базовый класс для работы с postgres."""

    def __init__(self, dbname: str, pg_user: str, password: str, host: str = 'localhost',
                 port: int = 5432, search_path: str = None):
        """
        :param dbname: название бд
        :param user: пользователь
        :param password: пароль
        :param host: хост
        :param port: порт
        :param search_path: установить порядок поиска в бд
        """
        self._pg_config = {
            'dbname': dbname,
            'user': pg_user,
            'password': password,
            'host': host,
            'port': port,
        }

        if search_path:
            self._pg_config['options'] = f'-c search_path={search_path}'

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def alive(self) -> bool:
        return True if (hasattr(self, 'connection') and not self.connection.closed) else False

    @backoff()
    def connect(self) -> object:
        """Соединяемся с бд или получаем уже имеющееся соединение"""
        if not hasattr(self, 'connection') or self.connection.closed:
            self.connection = psycopg2.connect(**self._pg_config)
        return self

    @backoff()
    def get_cursor(self) -> object:
        """Получаем курсор"""
        if not hasattr(self, 'cursor') or self.cursor.closed:
            self.cursor = self.connection.cursor(cursor_factory=extras.DictCursor)
        return self.cursor

    def close_connection(self) -> None:
        """Закрываем соединение с бд."""
        if hasattr(self, 'cursor') and not self.cursor.closed:
            self.cursor.close()
        if hasattr(self, 'connection') and not self.connection.closed:
            self.connection.close()

    @backoff()
    def execute(self, query: str, vars = None, err_msg: str = None) -> None:
        """Выполняем запрос
        :param query: запрос
        :param err_msg: сообщение в случае ошибки
        """
        try:
            if not hasattr(self, 'connection') or self.connection.closed:
                self.connect()
            if not hasattr(self, 'cursor') or self.cursor.closed:
                self.get_cursor()

            self.cursor.execute(query, vars)
            self.connection.commit()

        except InFailedSqlTransaction as err:

            log(f'Транзакция {query} привела к ошибке')
            self.connection.rollback()
            raise err

        except Exception as db_error:

            if not err_msg:
                err_msg = 'Ошибка при работе с бд\n'
            log(f'{err_msg}\nСкрипт, который пытались выполнить:\n{query}\n')
            raise db_error
