from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.api.v1 import openapi
from src.jwt import AuthJWT, login_required
from src.services.bookmarks_storage import (AbstractBookmarkStorage,
                                            get_bookmarks_storage)
from src.services.pagination import PaginationView, get_pagination_service

router = APIRouter(prefix='/bookmarks')


@router.post(
    '/{film_id}',
    **openapi.bookmarks.add_movie.dict(),
    status_code=HTTPStatus.CREATED
)
@login_required()
async def add_movie(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractBookmarkStorage = Depends(get_bookmarks_storage)
):
    """Добавляет фильм в закладки пользователя."""
    user_id = await authorize.get_jwt_subject()
    await storage.add(user_id, film_id)


@router.delete(
    '/{film_id}',
    **openapi.bookmarks.remove_movie.dict(),
    status_code=HTTPStatus.NO_CONTENT
)
@login_required()
async def remove_movie(
        film_id: UUID = Path(..., description='ID фильма'),
        authorize: AuthJWT = Depends(),
        storage: AbstractBookmarkStorage = Depends(get_bookmarks_storage)
):
    """Удаляет фильм из закладок пользователя."""
    user_id = await authorize.get_jwt_subject()
    await storage.remove(user_id, film_id)


@router.get(
    '/',
    **openapi.bookmarks.get_movies.dict()
)
@login_required()
async def get_movies(
        authorize: AuthJWT = Depends(),
        pagination: PaginationView = Depends(get_pagination_service),
        storage: AbstractBookmarkStorage = Depends(get_bookmarks_storage)
):
    """Получает список id фильмов, находящихся в закладках у пользователя."""
    user_id = await authorize.get_jwt_subject()
    return await storage.get(user_id, pagination.offset, pagination.size)
