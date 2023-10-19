# flake8: noqa:E501
from src.api.v1.openapi.base import BaseOpenapi

add_movie = BaseOpenapi(
    summary='Добавить фильм в закладки',
    description='Проверка существования фильма с переданным id не осуществляется',
    response_description=''
)

remove_movie = BaseOpenapi(
    summary='Удалить фильм из закладок',
    description='',
    response_description=''
)

get_movies = BaseOpenapi(
    summary='Получить список фильмов в закладках',
    description='Получение списка фильмов осуществляется учётом параметров пагинации',
    response_description='Список ID фильмов, находящихся в закладках'
)
