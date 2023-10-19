import pytest_asyncio
from tests.functional.testdata.test_data import Role


@pytest_asyncio.fixture()
async def make_role(make_http_request, get_roles_api_url):

    async def inner(role_data: Role.dict, authorization_token: str) -> dict:
        response = await make_http_request('POST', get_roles_api_url, token=authorization_token, data=role_data)
        return response

    return inner