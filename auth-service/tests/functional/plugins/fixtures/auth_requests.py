from http import HTTPStatus

import pytest_asyncio
from tests.functional.testdata.test_data import User


@pytest_asyncio.fixture()
async def login(make_http_request, get_auth_api_url):
    async def inner(user_data: dict, user_agent: str = 'default') -> dict:
        response = await make_http_request('POST', f'{get_auth_api_url}/login', headers={'User-Agent': user_agent},
                                           data={'login': user_data['login'], 'password': user_data['password']})
        return response

    return inner


@pytest_asyncio.fixture()
async def login_several_times(login):
    async def inner(count: int, user_data: dict, user_agent: str = 'default') -> dict:
        for _ in range(count - 1):
            await login(user_data, user_agent)
        response = await login(user_data, user_agent)
        return response

    return inner


@pytest_asyncio.fixture()
async def reg_user(make_http_request, get_auth_api_url):
    async def inner(user_data: dict) -> dict:
        response = await make_http_request('POST', f'{get_auth_api_url}/signup',
                                           data={'login': user_data['login'], 'password': user_data.get('password'),
                                                 'email': user_data.get('email'), 'full_name': user_data.get('full_name')})
        return response

    return inner


@pytest_asyncio.fixture()
async def reg_and_login(reg_user, login):
    async def inner(user_data: User.dict) -> dict:
        response = await reg_user({'login': user_data['login'], 'password': user_data['password'],
                                   'email': user_data.get('email'),
                                   'full_name': user_data['full_name']})
        assert response.status == HTTPStatus.OK

        response = await login({'login': user_data['login'], 'password': user_data['password']})
        return response

    return inner


@pytest_asyncio.fixture(scope="session")
async def logout(
        make_http_request,
        get_auth_api_url
):
    async def inner(access_token: str, user_agent: str = 'default'):
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        if user_agent:
            headers['User-Agent'] = user_agent
        url = f'{get_auth_api_url}/logout'
        return await make_http_request('POST', url, headers, None)

    return inner


@pytest_asyncio.fixture(scope="session")
async def logout_others(
        make_http_request,
        get_auth_api_url
):
    async def inner(access_token: str, user_agent: str = 'default'):
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        if user_agent:
            headers['User-Agent'] = user_agent
        url = f'{get_auth_api_url}/logout_others'
        return await make_http_request('POST', url, headers, None)

    return inner


@pytest_asyncio.fixture(scope="session")
async def refresh(
        make_http_request,
        get_auth_api_url
):
    async def inner(refresh_token: str, user_agent: str = 'default'):
        headers = {}
        if refresh_token:
            headers['Authorization'] = f'Bearer {refresh_token}'
        if user_agent:
            headers['User-Agent'] = user_agent
        url = f'{get_auth_api_url}/refresh'
        return await make_http_request('POST', url, headers, None)

    return inner