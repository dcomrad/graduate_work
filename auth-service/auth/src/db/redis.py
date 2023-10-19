from functools import cache
from hashlib import md5

from redis.asyncio import Redis
from src.core.config import settings
from src.db.base import AbstractTokenStorage


class RedisTokenStorage(AbstractTokenStorage):
    """Класс хранилища токенов, использующий в качестве места хранения No-SQL
    базу Redis."""
    def __init__(self, host: str, port: int):
        super().__init__(Redis(host=host, port=port))

    async def set_token(
            self,
            user: int,
            user_agent: str,
            token: str,
            expire_in_s: int = settings.jwt.authjwt_refresh_token_expires
    ) -> None:
        """См. описание метода в базовом классе."""
        await self.storage.set(self._make_key(user, user_agent),
                               token, ex=expire_in_s)
        await self.storage.sadd(user, user_agent)

    async def get_token(self, user: int, user_agent: str) -> str | None:
        """См. описание метода в базовом классе."""
        result = await self.storage.get(self._make_key(user, user_agent))
        return None if result is None else result.decode()

    async def delete_token(self, user: int, user_agent: str) -> None:
        """См. описание метода в базовом классе."""
        await self.storage.delete(self._make_key(user, user_agent))

    async def delete_tokens(
            self,
            user: int,
            exclude_user_agent: str | None = None
    ) -> None:
        """См. описание метода в базовом классе."""
        user_agents = await self.storage.smembers(user)
        if exclude_user_agent:
            user_agents.remove(exclude_user_agent.encode())
        if user_agents:
            await self.storage.srem(user, *user_agents)

        for user_agent in user_agents:
            await self.delete_token(user, user_agent.decode())

    async def close(self) -> None:
        """Метод разрывает соединение с Redis."""
        await self.storage.close()

    @staticmethod
    def _make_key(user: int, user_agent: str):
        """Метод хеширует составной ключ для использования в Redis."""
        return f'{user}:{md5(user_agent.encode("UTF-8")).hexdigest()}'


@cache
def get_token_storage() -> AbstractTokenStorage:
    """Возвращает объект хранилища. Применяется в dependency injection в
    эндпоинтах FastAPI."""
    return RedisTokenStorage(settings.redis.host, settings.redis.port)


token_storage = get_token_storage()
