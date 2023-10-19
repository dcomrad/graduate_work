from src.api.v1.openapi.base import BaseOpenapi

get = BaseOpenapi(
    summary='Информация об авторизованном пользователе',
    description=('Информация пользователя о самом себе'),
    response_description='Информация о пользователе'
)

update = BaseOpenapi(
    summary='Обновление данных пользователя',
    description=('Обновление личных данных пользователя'),
    response_description='Обновленные данные'
)

change_login = BaseOpenapi(
    summary='Изменение логина',
    description=('Изменение личного логина пользователем'),
    response_description='Обновленные данные'
)

change_password = BaseOpenapi(
    summary='Изменение пароля',
    description=('Изменение личного пароля пользователя'),
    response_description='True - если удаление прошло успешно. В случае неуспеха - ошибка'
)

access_history = BaseOpenapi(
    summary='История входов',
    description=('Возвращает историю входов пользователя. Входом считает '
                 'авторизация по логину и паролю (login).'),
    response_description='Перечень входов пользователя'
)
