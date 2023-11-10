import pytest

from functional.core.settings import tests_settings


@pytest.fixture(scope='session')
def get_subscriptions_url():
    return f'{tests_settings.service_url}/subscriptions'


@pytest.fixture(scope='session')
def get_customers_url():
    return f'{tests_settings.service_url}/customer'


@pytest.fixture(scope='session')
def get_backoffice_url():
    return f'{tests_settings.service_url}/backoffice'
