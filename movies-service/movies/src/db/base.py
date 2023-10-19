from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from src.services.view import ResponseView


class AbstractDataSource(ABC):
    def __init__(self, source: Any):
        self.source = source

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_collection(
            self,
            filter: Optional[dict],
            search: Optional[dict],
            view: ResponseView
    ) -> list[dict]:
        pass


class AbstractCacheStorage(ABC):
    def __init__(self):
        self.storage = 'storage'

    @abstractmethod
    async def get_cache_key(self, *args, **kwargs) -> str:
        pass

    @abstractmethod
    async def set_state(self, state_name: str, state: str, cache_expire_time: int) -> None:  # noqa:E501
        pass

    @abstractmethod
    async def get_state(self, state_name: str) -> str | None:
        pass


class AbstractFromCache(ABC):

    @classmethod
    @abstractmethod
    def set_storage_instance(cls, storage_instance) -> None:
        pass

    @classmethod
    @abstractmethod
    def _from_cache(cls):
        pass
