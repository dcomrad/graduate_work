from http import HTTPStatus

import pytest_asyncio
from tests.functional.testdata.test_data import Role, UserWithAccessPermissions
from tests.functional.utils.generate_test_data import gtd


async def test_roles_get_all(
        login,
        make_http_request,
        get_roles_api_url,
        make_role
):
    login_response = await login(UserWithAccessPermissions().dict())

    role_data_1 = gtd(Role(), 'name', 'description')
    role_data_2 = gtd(Role(), 'name', 'description')

    response_1 = await make_role(role_data_1, login_response.body['access'])
    assert response_1.body['name'] == role_data_1['name']

    response_2 = await make_role(role_data_2, login_response.body['access'])
    assert response_2.body['name'] == role_data_2['name']

    response = await make_http_request('GET', get_roles_api_url, token=login_response.body['access'])
    assert isinstance(response.body, list)

    number_roles_found = 0
    for r in response.body:
        if r['name'] in (role_data_1['name'], role_data_2['name']):
            number_roles_found += 1

    assert number_roles_found == 2


async def test_get_role(
        login,
        make_http_request,
        get_roles_api_url,
        make_role
):
    login_response = await login(UserWithAccessPermissions().dict())

    role_data = gtd(Role(), 'name', 'description')
    response = await make_role(role_data, login_response.body['access'])
    assert response.body['name'] == role_data['name']

    response = await make_http_request('GET', f'{get_roles_api_url}/{response.body["id"]}',
                                       token=login_response.body['access'])
    assert response.body['name'] == role_data['name']


async def test_update_role(
        login,
        make_http_request,
        get_roles_api_url,
        make_role
):
    login_response = await login(UserWithAccessPermissions().dict())

    role_data = gtd(Role(), 'name', 'description')
    role_response = await make_role(role_data, login_response.body['access'])

    new_role_name = gtd(Role(), 'name')['name']
    response = await make_http_request('PATCH', f'{get_roles_api_url}/{role_response.body["id"]}',
                                       token=login_response.body['access'],data={'name': new_role_name})
    assert response.body['name'] == new_role_name


async def test_delete_role(
        login,
        make_http_request,
        get_roles_api_url,
        make_role
):
    login_response = await login(UserWithAccessPermissions().dict())

    role_data = gtd(Role(), 'name', 'description')
    role_data = await make_role(role_data, login_response.body['access'])

    response = await make_http_request('DELETE', f'{get_roles_api_url}/{role_data.body["id"]}',
                                       token=login_response.body['access'])
    assert response.status == HTTPStatus.OK

    response = await make_http_request('GET', f'{get_roles_api_url}/{role_data.body["id"]}',
                                       token=login_response.body['access'])

    assert response.body == {'detail': 'Роль не найдена'}
