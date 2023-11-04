from src.api.v1.openapi.base import BaseOpenapi

refund = BaseOpenapi(
    summary='Возместить средства клиенту',
    description='Отправляет запрос платёжному провайдеру на возмещение средств'
)

cancel_subscription = BaseOpenapi(
    summary='Отменить подписку',
    description=('Отменяет автоматическое продление подписи после истечения '
                 'срока её действия')
)