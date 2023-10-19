from elasticsearch import BadRequestError, Elasticsearch
from elasticsearch.client import IndicesClient

from .tools.backoff import backoff
from .tools.logger import error, log


class ElasticManager:
    """Класс для работы с ElasticSearch"""

    def __init__(self, host, port, **indexes):
        self.host = host
        self.port = port
        self.indexes = {
            'film_work': indexes['film_work_index'],
            'person': indexes['persons_index'],
            'genre': indexes['genres_index']
        }

    def __enter__(self):
        self.connect_elastic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def alive(self):
        """Проверяем есть ли живое соединение"""
        return hasattr(self, 'client') and self.client.ping()

    def get_index_name_by_table_name(self, table_name):
        """Получаем название индекса"""
        return self.indexes[table_name]

    @backoff()
    def connect_elastic(self):
        """Подключаемся к Elastic"""
        try:
            if not hasattr(self, 'scheme'):
                self.scheme = 'http'
            if not isinstance(self.port, int):
                self.port = int(self.port)

            self.client = Elasticsearch([{'host': self.host, 'port': self.port, 'scheme': self.scheme}])
            log('Выполнили подключение к Elasticsearch')

            return self
        except Exception as err:
            error(f'Ошибка при подключении к Elastic.\n{err}\n\n')
            raise err

    @backoff()
    def create_index(self, index_name, index_scheme):
        """Создаем индекс
        :param index_name: название индекса
        :param index_scheme: схема индекса
        """
        try:
            IndicesClient(self.client).create(index=index_name, **index_scheme)
            log('Создали индекс')
        except BadRequestError:
            log('Индекс уже существует')

    def close(self):
        try:
            self.client.transport.close()
        except:
            pass

    @backoff()
    def save_data(self, table_name, data: list[dict]) -> None:
        """Сохраняем данные
        :param table_name: название таблица
        :param data: данные
        """
        try:
            if not hasattr(self, 'client') or not self.client.ping():
                self.connect_elastic()
            self.client.bulk(index=self.get_index_name_by_table_name(table_name), body=data, refresh=True)
        except Exception as err:
            error(f'Ошибка во время сохранения данных в Elastic.\n{err}\n\n')
            raise err
