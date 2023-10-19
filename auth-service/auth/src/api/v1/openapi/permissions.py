from src.api.v1.openapi.base import BaseOpenapi

get_all = BaseOpenapi(
    summary='Информация о всех доступах.',
    description=('Получение информации о всех доступах в виде списка.'),
    response_description='Список всех доступов, включающий id, имя доступа и его описание.'
)

get = BaseOpenapi(
    summary='Информация о доступе',
    description=('Получение информации о конкретном доступе, исходя из id переданного в адресной строке.'),
    response_description='Информация о доступе (id, name, description)'
)

create = BaseOpenapi(
    summary='Создание доступа',
    description=('Создание доступа по переданным в теле запроса параметрам.'),
    response_description='Информация о созданном доступе'
)

update = BaseOpenapi(
    summary='Изменение доступа',
    description=('Изменение данных о доступе'),
    response_description='Обновленная информация о доступе'
)

delete = BaseOpenapi(
    summary='Удаление доступа',
    description=('Удаления имеющегося доступа'),
    response_description='True - если удаление прошло успешно. В случае неуспеха - ошибка'
)
