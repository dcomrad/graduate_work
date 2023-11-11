import asyncio

import pytest


@pytest.fixture(scope='session')
def event_loop():
    el = asyncio.get_event_loop()
    yield el
    el.close()


pytest_plugins = [
    'functional.fixtures.api_fixtures',
    'functional.fixtures.url_fixtures',
]
