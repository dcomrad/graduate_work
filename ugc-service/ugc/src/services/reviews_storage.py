from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import motor.motor_asyncio as motor
from src.core.config import settings
from src.db.mongo_base import MongoBase
from src.services.base import AbstractReviewStorage
from src.services.rating_storage import MongoRatingStorage
from src.utils.exceptions import AlreadyExistsException, NotFoundException


class MongoReviewStorage(AbstractReviewStorage, MongoBase):
    def __init__(self, collection, rating_storage):
        self.rating_storage = rating_storage
        super().__init__(collection)

    async def add(self, user_id: int, film_id: UUID, review: Any) -> dict:
        _filter = {'user_id': user_id, 'film_id': film_id}
        if await self._check_if_exists(_filter):
            raise AlreadyExistsException('Такая рецензия уже существует')

        review = {
            '_id': uuid4(),
            'created_at': datetime.now(),
            **_filter,
            **review.dict()
        }
        await self.collection.insert_one(review)
        return review

    async def remove(self, user_id: int, film_id: UUID):
        review = await self.get(user_id, film_id)
        if review is None:
            raise NotFoundException('Такой рецензии не существует')

        await self.collection.delete_one({'_id': review['_id']})
        await self.rating_storage.remove_scores({'review_id': review['_id']})

    async def get(self, user_id: int, film_id: UUID) -> dict | None:
        _filter = {'user_id': user_id, 'film_id': film_id}
        return await self.collection.find_one(_filter)

    async def get_all(self, film_id: UUID) -> list[dict]:
        reviews = await self.collection.find({'film_id': film_id}).to_list(length=None)  # noqa:E501
        for review in reviews:
            likes, dislikes = await self.rating_storage.get_likes_and_dislikes(
                review['_id']
            )
            review.update({'likes': likes, 'dislikes': dislikes})
        return reviews

    async def like(self, user_id: int, review_id: UUID) -> None:
        await self._add_or_update_score(user_id, review_id,
                                        settings.project.like_score)

    async def dislike(self, user_id: int, review_id: UUID) -> None:
        await self._add_or_update_score(user_id, review_id,
                                        settings.project.dislike_score)

    async def remove_score(self, user_id: int, review_id: UUID) -> None:
        await self._add_or_update_score(user_id, review_id, None)

    async def _add_or_update_score(
            self,
            user_id: int,
            review_id: UUID,
            score: int | None
    ) -> None:
        _filter = {'user_id': user_id, '_id': review_id}
        if not await self._check_if_exists(_filter):
            raise NotFoundException('Такой рецензии не существует')

        if score is None:
            await self.rating_storage.remove_score(user_id, review_id)
        else:
            await self.rating_storage.add_or_update_score(
                user_id, review_id, score
            )


def get_reviews_storage() -> AbstractReviewStorage:
    client = motor.AsyncIOMotorClient(settings.mongo.connection_uri,
                                      uuidRepresentation='standard')
    database = motor.AsyncIOMotorDatabase(client, settings.mongo.dbname)

    return MongoReviewStorage(
        motor.AsyncIOMotorCollection(
            database, settings.mongo.reviews_collection
        ),

        MongoRatingStorage(
            motor.AsyncIOMotorCollection(
                database, settings.mongo.reviews_rating_collection
            ),
            'review_id'
        )
    )
