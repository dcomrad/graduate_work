from config.base_settings import auth_settings, billing_api_settings

USERS_AUTH_API_URL = (
    'http://'
    f'{auth_settings.host}:'
    f'{auth_settings.port}'
    '/api/v1/users'
)
REFUND_API_URL = (
    'http://'
    f'{billing_api_settings.host}:'
    f'{billing_api_settings.port}'
    '/api/v1/backoffice/refund'
)
CANCEL_SUB_API_URL = (
    'http://'
    f'{billing_api_settings.host}:'
    f'{billing_api_settings.port}'
    '/api/v1/backoffice/subscription'
)
