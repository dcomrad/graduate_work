from config.base_settings import auth_settings, billing_api_settings


def get_users_api_url():
    return f'http://{auth_settings.host}:{auth_settings.port}/api/v1/users'


def get_refund_api_url():
    return (
        f'http://{billing_api_settings.host}:{billing_api_settings.port}'
        '/api/v1/backoffice/refund'
    )


def get_cancel_sub_api_url():
    return (
        f'http://{billing_api_settings.host}:{billing_api_settings.port}'
        '/api/v1/backoffice/subscription'
    )
