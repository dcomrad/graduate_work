from src.api.v1.openapi.base import BaseOpenapi

get_all = BaseOpenapi(
    summary='Информация о всех ролях',
    description=('Получение информации о всех ролях в виде списка'),
    response_description='Список всех ролей'
)

get = BaseOpenapi(
    summary='Информация о роли',
    description=('Получение информации о конкретной роли'),
    response_description='Информация о роли'
)

get_role_permissions = BaseOpenapi(
    summary='Информация о доступах роли',
    description=('Получение информации о всем списке доступов для данной роли'),
    response_description='Информация о доступах для роли'
)

create = BaseOpenapi(
    summary='Создание роли',
    description=('Создание роли по переданным в теле запроса данным, с возможностью привязать к ней доступы'),
    response_description='Информация о созданной роли'
)

update = BaseOpenapi(
    summary='Изменение роли',
    description=('Изменение данных о роли'),
    response_description='Обновленная информация о роли'
)

delete = BaseOpenapi(
    summary='Удаление роли',
    description=('Удаление имеющейся роли'),
    response_description='True - если удаление прошло успешно. В случае неуспеха - ошибка'
)

remove_role_permissions = BaseOpenapi(
    summary='Удаление доступов для роли',
    description=('Удаление доступов для имеющейся роли'),
    response_description='Обновленная информация о роли'
)
