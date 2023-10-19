# flake8: noqa
from functools import wraps
from typing import Optional

from orjson import dumps, loads
from redis.asyncio import Redis
from src.core.config import settings
from src.db.base import AbstractCacheStorage, AbstractFromCache
from src.models import models_by_str

redis: Optional[Redis] = None


def get_redis() -> Redis:
    return redis


class RedisCacheStorage(AbstractCacheStorage):

    def __init__(self):
        self.storage = get_redis()

    @staticmethod
    async def get_cache_key(*args, **kwargs) -> str:
        """Получаем ключ для кэша"""
        return f"{args}{kwargs}"

    async def set_state(
            self,
            state_name: str,
            state: str,
            cache_expire_time: int = settings.project.cache_expire_time_s
    ) -> None:
        """Записываем кэш в редис
        :param state_name: ключ для хэша
        :param state: хэш (значение)
        :param cache_expire_time: "срок годности" кэша
        """
        await self.storage.set(state_name, state, ex=cache_expire_time)

    async def get_state(self, state_name: str) -> str | None:
        """Получаем кэш
        :param state_name: ключ для хэша
        """
        return await self.storage.get(state_name)


class cache(AbstractFromCache):

    @classmethod
    def set_storage_instance(cls, storage_instance) -> None:
        cls.storage = storage_instance

    @classmethod
    def _from_cache(cls, func):
        @wraps(func)
        async def inner(*args, **kwargs):
            nonlocal cls

            cache_structure = {
                'root_object_type': '',
                'cache': {
                    'model': '',
                    'data': '',
                }
            }

            cache_key = await cls.storage.get_cache_key(*args, **kwargs)
            _cache = await cls.storage.get_state(cache_key)

            if not _cache:
                _cache = await func(*args, **kwargs)
                if _cache is None:
                    return None

                if isinstance(_cache, (list, tuple)):
                    cache_structure['root_object_type'] = 'list'
                    cache_structure['cache'] = [
                        {'model': c.__class__.__name__.split('.')[-1],
                         'data': c.json(by_alias=True)}
                        for c in _cache
                    ]
                else:
                    cache_structure['root_object_type'] = 'single'
                    cache_structure['cache'] = {'model': _cache.__class__.__name__.split('.')[-1],
                                                'data': _cache.json(by_alias=True)}

                _cache = dumps(cache_structure)
                await cls.storage.set_state(state_name=cache_key, state=_cache)

            result = loads(_cache)
            if result['root_object_type'] == 'list':
                result = [models_by_str[r['model']].parse_raw(r['data']) for r in result['cache']]
            else:
                result = models_by_str[result['cache']['model']].parse_raw(result['cache']['data'])

            return result

        return inner
