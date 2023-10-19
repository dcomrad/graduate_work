from uuid import UUID

import motor.motor_asyncio as motor
from src.core.config import settings
from src.db.mongo_base import MongoBase
from src.services.base import AbstractBookmarkStorage
from src.utils.exceptions import AlreadyExistsException, NotFoundException


class MongoBookmarksStorage(MongoBase, AbstractBookmarkStorage):
    async def add(self, user_id: int, film_id: UUID):
        _filter = {'user_id': user_id, 'film_id': film_id}
        if await self._check_if_exists(_filter):
            raise AlreadyExistsException('Такая закладка уже существует')

        await self.collection.insert_one({**_filter})

    async def remove(self, user_id: int, film_id: UUID):
        _filter = {'user_id': user_id, 'film_id': film_id}
        if not await self._check_if_exists(_filter):
            raise NotFoundException('Такой закладки не существует')

        await self.collection.delete_one(_filter)

    async def get(self, user_id: int, offset: int, size: int) -> list[UUID]:
        bookmarks = await self.collection.find(
            {'user_id': user_id}
        ).skip(offset).limit(size).to_list(length=None)
        return [bookmark['film_id'] for bookmark in bookmarks]


def get_bookmarks_storage() -> AbstractBookmarkStorage:
    client = motor.AsyncIOMotorClient(settings.mongo.connection_uri,
                                      uuidRepresentation='standard')
    database = motor.AsyncIOMotorDatabase(client, settings.mongo.dbname)

    return MongoBookmarksStorage(
        motor.AsyncIOMotorCollection(
            database, settings.mongo.bookmarks_collection
        )
    )
