# flake8: noqa:E501
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from src.api.v1 import openapi
from src.core.utils import raise_404_if_none
from src.jwt import AuthJWT, login_required
from src.models.film import Film, FilmShortView
from src.services.collection import (CollectionService,
                                     get_film_collection_service)
from src.services.detail import DetailService, get_film_detail_service
from src.services.view import ResponseView, get_view_service

router = APIRouter(prefix='/films')


@router.get('/',
            response_model=list[FilmShortView],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.films.films.dict())
@login_required()
async def films(
        genre_id: Optional[UUID] = Query(None, description='ID жанра'),
        view_service: ResponseView = Depends(get_view_service),
        collection_service: CollectionService = Depends(get_film_collection_service),
        authorize: AuthJWT = Depends()
):
    """Возвращает фильмы с заданным параметром фильтрации и сортировки
    :param genre_id: id жанра, по которому фильтруется выдача
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    :param authorize: сервис, отвечающий за валидацию JWT токена
    """
    return await collection_service.get_collection(
        filter={'field': 'genre_id', 'value': genre_id},
        search=None,
        view=view_service
    )


@router.get('/search',
            response_model=list[FilmShortView],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.films.search_films.dict())
@login_required()
async def search_films(
        search_query: str = Query(..., description='Частичное или полное название фильма'),
        view_service: ResponseView = Depends(get_view_service),
        collection_service: CollectionService = Depends(get_film_collection_service),
        authorize: AuthJWT = Depends()
):
    """Возвращает фильмы, отфильтрованные поиском по полю title
    :param search_query: частичное или полное название фильма
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    :param authorize: сервис, отвечающий за валидацию JWT токена
    """
    return await collection_service.get_collection(
        filter=None,
        search={'field': 'title', 'query': search_query},
        view=view_service
    )


@router.get('/{film_id}',
            response_model=Film,
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.films.film_details.dict())
@login_required()
async def film_details(
        film_id: UUID = Path(..., description='ID фильма'),
        detail_service: DetailService = Depends(get_film_detail_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает фильм по его id
    :param film_id: id искомого фильма
    :param detail_service: сервис, отвечающий за получение одного фильма
    :param authorize: сервис, отвечающий за валидацию JWT токена
    """
    film = await detail_service.get_by_id(film_id)
    raise_404_if_none(film)

    return film


@router.get('/{film_id}/similar',
            response_model=list[FilmShortView],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.films.similar_films.dict())
@login_required()
async def similar_films(
        film_id: UUID = Path(..., description='ID фильма'),
        view_service: ResponseView = Depends(get_view_service),
        detail_service: DetailService = Depends(get_film_detail_service),
        collection_service: CollectionService = Depends(get_film_collection_service),
        authorize: AuthJWT = Depends()
):
    """Возвращает фильмы, имеющие жанры, аналогичные заданному фильму
    :param film_id: id фильма, из которого берутся жанры
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param detail_service: сервис, отвечающий за получение одного элемента
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    :param authorize: сервис, отвечающий за валидацию JWT токена
    """
    film = await detail_service.get_by_id(film_id)
    raise_404_if_none(film)

    return await collection_service.get_collection(
        filter={'field': 'genre_id', 'value': [genre.uuid for genre in film.genres]},
        search=None,
        view=view_service
    )
