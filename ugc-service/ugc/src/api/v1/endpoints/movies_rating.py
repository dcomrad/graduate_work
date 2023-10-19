from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from src.api.v1 import openapi
from src.jwt import AuthJWT, login_required
from src.services.rating_storage import (AbstractRatingStorage,
                                         get_movies_rating_storage)

router = APIRouter(prefix='/movies-rating')


@router.post(
    '/{film_id}',
    **openapi.movies_rating.add_or_update_score.dict(),
    status_code=HTTPStatus.CREATED
)
@login_required()
async def add_or_update_score(
        film_id: UUID = Path(..., description='ID фильма'),
        score: int = Query(..., ge=0, le=10, description='Оценка фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractRatingStorage = Depends(get_movies_rating_storage)
):
    """Добавляет или обновляет оценку, выставленную пользователем фильму."""
    user_id = await authorize.get_jwt_subject()
    await storage.add_or_update_score(user_id, film_id, score)


@router.delete(
    '/{film_id}',
    **openapi.movies_rating.remove_score.dict(),
    status_code=HTTPStatus.NO_CONTENT
)
@login_required()
async def remove_score(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractRatingStorage = Depends(get_movies_rating_storage)
):
    """Удаляет оценку, выставленную пользователем фильму."""
    user_id = await authorize.get_jwt_subject()
    await storage.remove_score(user_id, film_id)


@router.get(
    '/{film_id}/likes_and_dislikes',
    **openapi.movies_rating.get_likes_and_dislikes.dict()
)
@login_required()
async def get_likes_and_dislikes(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),  # noqa
        storage: AbstractRatingStorage = Depends(get_movies_rating_storage)
):
    """Получает список лайков и дизлайков для фильма."""
    likes, dislikes = await storage.get_likes_and_dislikes(film_id)
    return {'likes': likes, 'dislikes': dislikes}


@router.get(
    '/{film_id}/avg_score',
    **openapi.movies_rating.get_avg_score.dict()
)
@login_required()
async def get_avg_score(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),  # noqa
        storage: AbstractRatingStorage = Depends(get_movies_rating_storage)
):
    """Получает среднюю оценку для фильма."""
    avg_score = await storage.get_avg_score(film_id)
    return {'avg_score': avg_score}
