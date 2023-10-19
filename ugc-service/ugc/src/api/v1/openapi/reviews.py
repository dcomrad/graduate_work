from src.api.v1.openapi.base import BaseOpenapi

add = BaseOpenapi(
    summary='Добавить рецензию к фильму',
    description='',
    response_description='Вновь добавленная рецензия'
)

remove = BaseOpenapi(
    summary='Удалить рецензию',
    description='',
    response_description=''
)

get = BaseOpenapi(
    summary='Получить все рецензии к фильму',
    description='',
    response_description='Список рецензий к фильму'
)

like = BaseOpenapi(
    summary='Поставить рецензии лайк',
    description='Осуществляется проверка существования рецензии по id',
    response_description=''
)

dislike = BaseOpenapi(
    summary='Поставить рецензии дизлайк',
    description='Осуществляется проверка существования рецензии по id',
    response_description=''
)

remove_score = BaseOpenapi(
    summary='Удалить выставленный лайк/дизлайк у рецензии',
    description='',
    response_description=''
)
