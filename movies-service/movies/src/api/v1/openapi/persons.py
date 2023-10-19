from src.api.v1.openapi.base import BaseOpenapi

search_persons = BaseOpenapi(
    summary='Поиск человека',
    description=('Отображает найденных по запросу людей. Возможна сортировка '
                 'по некоторым полям, а также пагинация результата запроса.'),
    response_description='Список с подробной информацией о людях'
)

person_details = BaseOpenapi(
    summary='Подробности о человеке',
    description='Отображает подробную информацию о человеке по заданному ID.',
    response_description='Подробная информация о человеке'
)

person_films = BaseOpenapi(
    summary='Список фильмов с участием конкретного человека',
    description=('Отображает фильмы, в работе над которым принимал участие '
                 'заданный человек. Возможна сортировка по некоторым полям, а '
                 'также пагинация результата запроса.'),
    response_description='Список с краткой информацией о фильмах'
)
