from src.api.v1.openapi.base import BaseOpenapi

get_all_payment_methods = BaseOpenapi(
    summary='Получить список способов оплат',
    description=('Предоставляются способы оплаты только того клиента, от '
                 'которого пришёл запрос'),
    response_description='Список всех сохранённых способов оплат клиента'
)

add_payment_method = BaseOpenapi(
    summary='Добавить способ оплаты',
    description=('Отправляет запрос платёжному провайдеру на добавление '
                 'нового способа оплаты. Способ оплаты добавляется '
                 'пользователю, от которого пришёл запрос'),
    response_description='HTML-форма добавления способа оплаты'
)

set_default_payment_method = BaseOpenapi(
    summary='Установить способ оплаты по-умолчанию',
    description=('Устанавливает указанный способ оплаты в качество способа '
                 'по-умолчанию'),
)

remove_payment_method = BaseOpenapi(
    summary='Удалить способ оплаты',
    description=('Направляет запрос платёжному провайдеру на удаление ранее '
                 'сохранённого способа оплаты'),
)

get_subscription = BaseOpenapi(
    summary='Получить текущую подписку',
    description='Информация пользователя о самом себе',
    response_description='Информация о подписке пользователя'
)

subscribe = BaseOpenapi(
    summary='Оформить подписку',
    description=('Направляет запрос платёжному провайдеру на списание средств '
                 'с указанного способа оплаты за указанную подписку'),
)

unsubscribe = BaseOpenapi(
    summary='Отменить подписку',
    description='Отменяет автоматическое продление подписки',
)

get_transactions = BaseOpenapi(
    summary='Получить список транзакций',
    description=('Предоставляются транзакции только того клиента, от которого '
                 'пришёл запрос'),
    response_description=('Список всех транзакций пользователя, '
                          'отсортированных по убыванию даты создания')
)
