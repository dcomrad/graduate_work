from src.api.v1.openapi.base import BaseOpenapi

get_all = BaseOpenapi(
    summary='Информация о всех пользователях',
    description=('Получение информации о всех пользователях в системе'),
    response_description='Список пользователей'
)

get = BaseOpenapi(
    summary='Информация о конкретном пользователе',
    description=('Информация о конкретном пользователе по его id'),
    response_description='Информация о пользователе'
)

update = BaseOpenapi(
    summary='Обновление данных пользователя',
    description=('Обновление данных в системе о пользователе'),
    response_description='Обновленные данные'
)

remove_user_roles = BaseOpenapi(
    summary='Удаление ролей у пользователя',
    description=('Удаление выбранных ролей у пользователя по его id'),
    response_description='Обновленная информация о пользователе'
)
