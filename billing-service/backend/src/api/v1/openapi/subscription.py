from src.api.v1.openapi.base import BaseOpenapi

get_all = BaseOpenapi(
    summary='Получить список подписок',
    description='Предоставляются сведения только об активных подписках',
    response_description='Список всех активных подписок'
)

get = BaseOpenapi(
    summary='Получить сведения о конкретной подписке',
    description='Информация предоставляется только если подписка активна',
    response_description='Информация о подписке'
)
