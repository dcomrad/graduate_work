from src.api.v1.openapi.base import BaseOpenapi

genres = BaseOpenapi(
    summary='Список жанров',
    description=('Отображает все жанры. Возможна сортировка по некоторым '
                 'полям, а также пагинация результата запроса.'),
    response_description='Список с подробной информацией о жанрах'
)

genre_details = BaseOpenapi(
    summary='Подробности о жанре',
    description='Отображает подробную информацию о жанре по заданному ID.',
    response_description='Подробная информация о жанре'
)
