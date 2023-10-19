from abc import ABC, abstractmethod
from typing import Any

DATABASE_URL_TEMPLATE = '{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'


class AbstractTokenStorage(ABC):
    """Абстратный класс, представляющий хранилище токенов."""
    def __init__(self, storage: Any):
        self.storage = storage

    @abstractmethod
    async def set_token(
            self,
            user: int,
            user_agent: str,
            token: str,
            expire_in_s: int
    ) -> None:
        """Метод сохранения токена пользователя в хранилище.
        :param user - идентификатор пользователя.
        :param user_agent - название пользовательского приложения, с которого
        пришёл запрос.
        :param token - токен пользователя.
        :param expire_in_s - время жизни токена в хранилище (в секундах).
        """
        pass

    @abstractmethod
    async def get_token(self, user: int, user_agent: str) -> str | None:
        """Метод получения токена пользователя из хранилища.
        :param user - идентификатор пользователя.
        :param user_agent - название пользовательского приложения, с которого
        пришёл запрос.
        """
        pass

    @abstractmethod
    async def delete_token(self, user: int, user_agent: str) -> None:
        """Метод удаления токена пользователя из хранилища.
        :param user - идентификатор пользователя.
        :param user_agent - название пользовательского приложения, с которого
        пришёл запрос.
        """
        pass

    @abstractmethod
    async def delete_tokens(
            self,
            user: int,
            exclude_user_agent: None | str = None
    ) -> None:
        """Метод удаления всех токенов пользователя из хранилища.
        :param user - идентификатор пользователя.
        :param exclude_user_agent - название пользовательского приложения, с
        которого пришёл запрос и к которому привязан один из пользовательских
        токенов, который не нужно удалять."""
        pass
