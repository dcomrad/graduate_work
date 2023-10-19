from uuid import UUID

import motor.motor_asyncio as motor
from src.core.config import settings
from src.db.mongo_base import MongoBase
from src.services.base import AbstractRatingStorage
from src.utils.exceptions import NotFoundException


class MongoRatingStorage(MongoBase, AbstractRatingStorage):
    def __init__(self, collection, scored_field_name: str):
        self.scored_field_name = scored_field_name
        super().__init__(collection)

    async def add_or_update_score(self, user_id: int, obj_id: UUID, score: int):  # noqa:E501
        _filter = {'user_id': user_id, self.scored_field_name: obj_id}
        await self.collection.replace_one(
            _filter, {'score': score, **_filter}, upsert=True
        )

    async def remove_score(self, user_id: int, obj_id: UUID) -> None:
        _filter = {'user_id': user_id, self.scored_field_name: obj_id}
        await self._check_if_exists(_filter)
        await self.collection.delete_one(_filter)

    async def remove_scores(self, _filter: dict) -> None:
        await self.collection.delete_many(_filter)

    async def get_likes_and_dislikes(self, obj_id: UUID) -> tuple[int, int]:
        likes_amount = await self.collection.count_documents(
            {
                self.scored_field_name: obj_id,
                'score': settings.project.like_score
            }
        )
        dislikes_amount = await self.collection.count_documents(
            {
                self.scored_field_name: obj_id,
                'score': settings.project.dislike_score
            }
        )
        return likes_amount, dislikes_amount

    async def get_avg_score(self, obj_id: UUID) -> float | None:
        await self._check_if_exists({self.scored_field_name: obj_id})
        avg_result = await self.collection.aggregate([
            {'$match': {self.scored_field_name: obj_id}},
            {'$group': {
                '_id': 'score',
                'avg_score': {
                    '$avg': '$score'
                }
            }}
        ]).to_list(length=None)
        if avg_result:
            return avg_result[0]['avg_score']
        return None

    async def _check_if_exists(self, _filter: dict) -> None:
        if not await super()._check_if_exists(_filter):
            message = (
                'Нет ни одной оценки для '
                f'{self.scored_field_name}={_filter[self.scored_field_name]}'
            )
            raise NotFoundException(message)


def get_movies_rating_storage() -> AbstractRatingStorage:
    client = motor.AsyncIOMotorClient(settings.mongo.connection_uri,
                                      uuidRepresentation='standard')
    database = motor.AsyncIOMotorDatabase(client, settings.mongo.dbname)

    return MongoRatingStorage(
        motor.AsyncIOMotorCollection(
            database, settings.mongo.movies_rating_collection
        ),
        'film_id'
    )
