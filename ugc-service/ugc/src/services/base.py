from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class AbstractBroker(ABC):
    """Базовый класс брокера сообщений."""
    def __init__(self, broker: Any):
        self.broker = broker

    @abstractmethod
    async def send(self, user_id: int, film_id: UUID, timestamp: int):
        pass


class AbstractProgressStorage(ABC):
    """Абстратный класс, представляющий хранилище сведений о времени просмотра
    кинопроизведений."""
    def __init__(self, storage: Any):
        self.storage = storage

    @abstractmethod
    async def get(self, user_id: int, film_id: UUID) -> int | None:
        pass


class AbstractBookmarkStorage(ABC):
    """Абстратный класс, представляющий хранилище закладок пользователей."""
    @abstractmethod
    async def add(self, user_id: int, film_id: UUID):
        pass

    @abstractmethod
    async def remove(self, user_id: int, film_id: UUID):
        pass

    @abstractmethod
    async def get(self, user_id: int, offset: int, size: int) -> list[UUID]:
        pass


class AbstractRatingStorage(ABC):
    """Абстрактный класс, представляющий хранилище рейтинга."""
    @abstractmethod
    async def add_or_update_score(self, user_id: int, obj_id: UUID, score: int):  # noqa:E501
        pass

    @abstractmethod
    async def remove_score(self, user_id: int, obj_id: UUID):
        pass

    @abstractmethod
    async def get_likes_and_dislikes(self, obj_id: UUID) -> tuple[int, int]:
        pass

    @abstractmethod
    async def get_avg_score(self, obj_id: UUID) -> float | None:
        pass


class AbstractReviewStorage(ABC):
    """Абстратный класс, представляющий хранилище рецензий."""
    @abstractmethod
    async def add(self, user_id: int, film_id: UUID, review: Any) -> dict:
        pass

    @abstractmethod
    async def remove(self, user_id: int, film_id: UUID):
        pass

    @abstractmethod
    async def get(self, user_id: int, film_id: UUID) -> Any:
        pass

    @abstractmethod
    async def get_all(self, film_id: UUID) -> list[Any]:
        pass

    @abstractmethod
    async def like(self, user_id: int, review_id: UUID):
        pass

    @abstractmethod
    async def dislike(self, user_id: int, review_id: UUID):
        pass

    @abstractmethod
    async def remove_score(self, user_id: int, review_id: UUID):
        pass
