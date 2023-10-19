import pytest_asyncio
from tests.functional.testdata.test_data import Permission


@pytest_asyncio.fixture()
async def make_permission(make_http_request, get_permissions_api_url):

    async def inner(permission_data: Permission, authorization_token: str) -> dict:
        response = await make_http_request('POST', get_permissions_api_url,
                                           token=authorization_token, data=permission_data)
        return response

    return inner