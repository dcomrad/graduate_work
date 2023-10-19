import asyncio
import os

import pytest


@pytest.fixture(scope="session")
def event_loop():
    el = asyncio.get_event_loop()
    yield el
    el.close()


pytest_plugins = [
    'tests.functional.plugins.fixtures.'+fixture_file.replace(".py", "")
    for fixture_file in os.listdir(f"{os.path.dirname(__file__)}/plugins/fixtures/")
]
