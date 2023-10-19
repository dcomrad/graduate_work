from functools import cache
from uuid import UUID

from redis.asyncio import Redis
from src.core.config import settings
from src.services.base import AbstractProgressStorage


class RedisProgressStorage(AbstractProgressStorage):
    def __init__(self, host: str, port: int):
        super().__init__(Redis(host=host, port=port))

    async def get(self, user_id: int, film_id: UUID) -> int | None:
        """См. описание метода в базовом классе."""
        result = await self.storage.get(self._make_key(user_id, film_id))
        return int(result) if result else result

    @staticmethod
    def _make_key(user_id: int, film_id: UUID):
        return f'{user_id}+{film_id}'


@cache
def get_progress_storage() -> AbstractProgressStorage:
    return RedisProgressStorage(settings.redis.host, settings.redis.port)
