# flake8: noqa:E501
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from src.api.v1 import openapi
from src.core.utils import raise_404_if_none
from src.jwt import AuthJWT, login_required
from src.models import FilmShortView, Person
from src.services.collection import (CollectionService,
                                     get_film_collection_service,
                                     get_person_collection_service)
from src.services.detail import DetailService, get_person_detail_service
from src.services.view import ResponseView, get_view_service

router = APIRouter(prefix='/persons')


@router.get('/search',
            response_model=list[Person],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.persons.search_persons.dict())
@login_required()
async def search_persons(
        search_query: str = Query(..., description='Частичное или полное имя человека'),
        view_service: ResponseView = Depends(get_view_service),
        collection_service: CollectionService = Depends(get_person_collection_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает людей, отфильтрованных поиском по полю full_name
    :param search_query: частичное или полное имя человека
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    """
    return await collection_service.get_collection(
        filter=None,
        search={'field': 'full_name', 'query': search_query},
        view=view_service
    )


@router.get('/{person_id}',
            response_model=Person,
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.persons.person_details.dict())
@login_required()
async def person_details(
        person_id: UUID = Path(..., description='ID человека'),
        detail_service: DetailService = Depends(get_person_detail_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает человека по его id
    :param person_id: id искомого человека
    :param detail_service: сервис, отвечающий за получение одного элемента
    """
    item = await detail_service.get_by_id(person_id)
    raise_404_if_none(item)

    return item


@router.get('/{person_id}/film',
            response_model=list[FilmShortView],
            response_model_exclude_none=True,
            response_model_by_alias=False,
            **openapi.persons.person_films.dict())
@login_required()
async def person_films(
        person_id: UUID = Path(..., description='ID человека'),
        view_service: ResponseView = Depends(get_view_service),
        detail_service: DetailService = Depends(get_person_detail_service),
        collection_service: CollectionService = Depends(get_film_collection_service),
        authorize: AuthJWT = Depends(), # noqa
):
    """Возвращает фильмы, в работе над которым принимал участие заданный
    человек.
    :param person_id: id персоны для поиска фильмов
    :param view_service: сервис, отвечающий за представление коллекции (сортировка, пагинация)
    :param detail_service: сервис, отвечающий за получение одного элемента
    :param collection_service: сервис, отвечающий за получение коллекции элементов
    """
    person = await detail_service.get_by_id(person_id)
    raise_404_if_none(person)

    return await collection_service.get_collection(
        filter={'field': 'person_id', 'value': person_id},
        search=None,
        view=view_service
    )
