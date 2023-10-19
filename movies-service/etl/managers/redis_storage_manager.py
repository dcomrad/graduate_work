from typing import Any, Callable

from redis import Redis

from .tools.backoff import backoff


class RedisStorage:
    """Класс для работы с Redis."""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port

    def connect(self):
        self.connection = Redis(host=self.host, port=self.port)
        return self

    def close(self):
        try:
            self.connection.close()
        except:
            pass

    def alive(self) -> bool:
        """Проверяем подключение"""
        return hasattr(self, 'connection') and self.connection.ping()

    @backoff()
    def execute(self, func: Callable) -> Any:
        if not self.alive():
            self.connect()
        return func()

    def save_state(self, state, value) -> None:
        """Сохранить состояние в хранилище."""
        self.execute(lambda: self.connection.set(state, value))

    def retrieve_state(self, param) -> Any:
        """Получить состояние из хранилища."""
        result = self.execute(lambda: self.connection.get(param))
        return result.decode() if result else result


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage) -> None:
        self.storage = storage

    def __enter__(self):
        self.storage.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.close()

    def alive(self) -> bool:
        """Проверяем подключение"""
        return self.storage.alive()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.storage.save_state(key, value)

    def get_last_state(self, table_name: str) -> str:
        """Получаем время последних загруженных данных.
        :param state: время загруженных данных
        """
        current_state = self.storage.retrieve_state(table_name)
        if not current_state:
            current_state = '0001-01-01 00:00:00.000000+00:00'
        return current_state
