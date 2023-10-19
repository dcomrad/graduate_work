from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Response
from src.api.v1 import openapi
from src.jwt import AuthJWT, login_required
from src.schemas import ReviewCreate
from src.services.reviews_storage import (AbstractReviewStorage,
                                          get_reviews_storage)

router = APIRouter(prefix='/reviews')


@router.post(
    '/{film_id}',
    **openapi.reviews.add.dict(),
    status_code=HTTPStatus.CREATED
)
@login_required()
async def add(
        review: ReviewCreate,
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Добавляет рецензию пользователя к фильму."""
    user_id = await authorize.get_jwt_subject()
    return await storage.add(user_id, film_id, review)


@router.delete(
    '/{film_id}',
    **openapi.reviews.remove.dict(),
    status_code=HTTPStatus.NO_CONTENT
)
@login_required()
async def remove(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Удаляет рецензию пользователя к фильму."""
    user_id = await authorize.get_jwt_subject()
    await storage.remove(user_id, film_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get(
    '/{film_id}',
    **openapi.reviews.get.dict()
)
async def get(
        film_id: UUID = Path(..., description='ID фильма'),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Получает все рецензии к фильму."""
    return await storage.get_all(film_id)


@router.post(
    '/{review_id}/like',
    **openapi.reviews.like.dict(),
    status_code=HTTPStatus.CREATED
)
@login_required()
async def like(
        review_id: UUID = Path(..., description='ID рецензии'),
        authorize: AuthJWT = Depends(),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Добавляет лайк к рецензии."""
    user_id = await authorize.get_jwt_subject()
    await storage.like(user_id, review_id)


@router.post(
    '/{review_id}/dislike',
    **openapi.reviews.dislike.dict(),
    status_code=HTTPStatus.CREATED
)
@login_required()
async def dislike(
        review_id: UUID = Path(..., description='ID рецензии'),
        authorize: AuthJWT = Depends(),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Добавляет дизлайк к рецензии."""
    user_id = await authorize.get_jwt_subject()
    await storage.dislike(user_id, review_id)


@router.delete(
    '/{review_id}/remove_score',
    **openapi.reviews.remove_score.dict(),
    status_code=HTTPStatus.NO_CONTENT
)
@login_required()
async def remove_score(
        review_id: UUID = Path(..., description='ID рецензии'),
        authorize: AuthJWT = Depends(),
        storage: AbstractReviewStorage = Depends(get_reviews_storage)
):
    """Удаляет оценку к рецензии."""
    user_id = await authorize.get_jwt_subject()
    await storage.remove_score(user_id, review_id)
