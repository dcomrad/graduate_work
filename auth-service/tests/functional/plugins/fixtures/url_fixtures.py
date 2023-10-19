import pytest
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
def get_auth_api_url():
    return f'http://{test_settings.auth.host}:{test_settings.auth.port}/api/v1/auth'


@pytest.fixture(scope='session')
def get_user_api_url():
    return f'http://{test_settings.auth.host}:{test_settings.auth.port}/api/v1/me'


@pytest.fixture(scope='session')
def get_users_api_url():
    return f'http://{test_settings.auth.host}:{test_settings.auth.port}/api/v1/users'


@pytest.fixture(scope='session')
def get_roles_api_url():
    return f'http://{test_settings.auth.host}:{test_settings.auth.port}/api/v1/roles'


@pytest.fixture(scope='session')
def get_permissions_api_url():
    return f'http://{test_settings.auth.host}:{test_settings.auth.port}/api/v1/permissions'
