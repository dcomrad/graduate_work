from config.base_settings import auth_settings


def get_users_api_url():
    return f'http://{auth_settings.host}:{auth_settings.port}/api/v1/users'
