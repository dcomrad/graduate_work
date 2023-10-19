# flake8: noqa:501
from src.api.v1.openapi.base import BaseOpenapi

add_or_update_score = BaseOpenapi(
    summary='Добавить или изменить оценку фильму',
    description='Проверка существования фильма с переданным id не осуществляется',
    response_description=''
)

remove_score = BaseOpenapi(
    summary='Удалить выставленную оценку фильму',
    description='',
    response_description=''
)

get_likes_and_dislikes = BaseOpenapi(
    summary='Получить количество лайков и дизлайков у фильма',
    description='',
    response_description='Количество лайков и дизлайков'
)

get_avg_score = BaseOpenapi(
    summary='Получить среднюю оценку фильма',
    description='',
    response_description='Средняя оценка фильма'
)
