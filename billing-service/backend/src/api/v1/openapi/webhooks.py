from src.api.v1.openapi.base import BaseOpenapi

stripe_webhook = BaseOpenapi(
    summary='Получить уведомление от Stripe',
    description=('Вебхук для получения уведомлений от платёжного провайдера '
                 'Stripe')
)
