# flake8: noqa:E501
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.api.v1 import openapi
from src.core.utils import raise_404_if_none
from src.jwt import AuthJWT, login_required
from src.models.genre import Genre
from src.services.collection import (CollectionService,
                                     get_genre_collection_service)
from src.services.detail import DetailService, get_genre_detail_service
from src.services.view import ResponseView, get_view_service

router = APIRouter(prefix='/genres')


@router.get('/',
            response_model=list[Genre],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.genres.genres.dict())
@login_required()
async def genres(
        view_service: ResponseView = Depends(get_view_service),
        collection_service: CollectionService = Depends(get_genre_collection_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает все жанры.
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    """
    return await collection_service.get_collection(
        filter=None,
        search=None,
        view=view_service
    )


@router.get('/{genre_id}',
            response_model=Genre,
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.genres.genre_details.dict())
@login_required()
async def genre_details(
        genre_id: UUID = Path(..., description='ID жанра'),
        detail_service: DetailService = Depends(get_genre_detail_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает жанр по его id
    :param genre_id: id искомого жанра
    :param detail_service: сервис, отвечающий за получение одного элемента
    """
    genre = await detail_service.get_by_id(genre_id)
    raise_404_if_none(genre)

    return genre
