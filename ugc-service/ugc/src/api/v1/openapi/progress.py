from src.api.v1.openapi.base import BaseOpenapi

push_movie_timestamp = BaseOpenapi(
    summary='Добавить данные о текушем времени просмотра кинопроизведения',
    description='Добавление происходит в брокер сообщений Kafka',
    response_description=''
)

fetch_movie_timestamp = BaseOpenapi(
    summary='Получить данные о текушем времени просмотра кинопроизведения',
    description='',
    response_description='Количество просмотренных секунд кинопроизведения'
)
