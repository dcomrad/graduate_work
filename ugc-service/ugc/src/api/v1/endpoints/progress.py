from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from src.api.v1 import openapi
from src.jwt import AuthJWT, login_required
from src.services.broker import AbstractBroker, get_broker
from src.services.progress_storage import (AbstractProgressStorage,
                                           get_progress_storage)

router = APIRouter(prefix='/progress')


@router.post(
    '/{film_id}',
    **openapi.progress.push_movie_timestamp.dict(),
    status_code=HTTPStatus.ACCEPTED
)
@login_required()
async def push_movie_timestamp(
        film_id: UUID = Path(..., description='ID просматриваемого фильма'),
        timestamp: int = Query(..., ge=0, description='Номер просмотренной секунды'),  # noqa:E501
        authorize: AuthJWT = Depends(),
        broker: AbstractBroker = Depends(get_broker)
):
    """Отправляет в брокер сообщений информацию о времени просмотра фильма."""
    user_id = await authorize.get_jwt_subject()
    await broker.send(user_id, film_id, timestamp)


@router.get(
    '/{film_id}',
    **openapi.progress.fetch_movie_timestamp.dict()
)
@login_required()
async def fetch_movie_timestamp(
        film_id: UUID = Path(..., description='ID просматриваемого фильма'),
        authorize: AuthJWT = Depends(),
        progress_storage: AbstractProgressStorage = Depends(get_progress_storage),  # noqa:E501
):
    """Получает информацию о времени просмотра фильма."""
    user_id = await authorize.get_jwt_subject()
    timestamp = await progress_storage.get(user_id, film_id)
    return {'film_id': film_id, 'timestamp': timestamp}
