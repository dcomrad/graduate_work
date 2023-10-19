from http import HTTPStatus

import pytest_asyncio
from tests.functional.testdata.test_data import (Permission,
                                                 UserWithAccessPermissions)
from tests.functional.utils.generate_test_data import gtd


async def test_permissions_get_all(
        login,
        make_http_request,
        get_permissions_api_url,
        make_permission
):
    login_response = await login(UserWithAccessPermissions().dict())

    permission_data_1 = gtd(Permission(), 'name', 'description')
    permission_data_2 = gtd(Permission(), 'name', 'description')

    response_1 = await make_permission(permission_data_1, login_response.body['access'])
    assert response_1.body['name'] == permission_data_1['name']

    response_2 = await make_permission(permission_data_2, login_response.body['access'])
    assert response_2.body['name'] == permission_data_2['name']

    response = await make_http_request('GET', get_permissions_api_url, token=login_response.body['access'])
    assert isinstance(response.body, list)

    number_permissions_found = 0
    for r in response.body:
        if r['name'] in (permission_data_1['name'], permission_data_2['name']):
            number_permissions_found += 1

    assert number_permissions_found == 2


async def test_get_permission(
        login,
        make_http_request,
        get_permissions_api_url,
        make_permission
):
    login_response = await login(UserWithAccessPermissions().dict())

    permission_data = gtd(Permission(), 'name', 'description')
    response = await make_permission(permission_data, login_response.body['access'])
    assert response.body['name'] == permission_data['name'] # TODO по идее, этого тут не должно быть, мы просто подготавливаемся к другому тесту

    response = await make_http_request('GET', f'{get_permissions_api_url}/{response.body["id"]}',
                                       token=login_response.body['access'])
    assert response.body['name'] == permission_data['name']


async def test_update_permission(
        login,
        make_http_request,
        get_permissions_api_url,
        make_permission
):
    login_response = await login(UserWithAccessPermissions().dict())

    permission_data = gtd(Permission(), 'name', 'description')
    permission_response = await make_permission(permission_data, login_response.body['access'])

    new_permission_name = gtd(Permission(), 'name')['name']
    response = await make_http_request('PATCH', f'{get_permissions_api_url}/{permission_response.body["id"]}',
                                       token=login_response.body['access'],
                                       data={'name': new_permission_name})
    assert response.body['name'] == new_permission_name


async def test_delete_permission(
        login,
        make_http_request,
        get_permissions_api_url,
        make_permission
):
    login_response = await login(UserWithAccessPermissions().dict())

    permission_data = gtd(Permission(), 'name', 'description')
    permission_data = await make_permission(permission_data, login_response.body['access'])

    response = await make_http_request('DELETE', f'{get_permissions_api_url}/{permission_data.body["id"]}',
                                       token=login_response.body['access'])
    assert response.status == HTTPStatus.OK

    response = await make_http_request('GET', f'{get_permissions_api_url}/{permission_data.body["id"]}',
                                       token=login_response.body['access'])

    assert response.body == {'detail': 'Такое разрешение не найдено'}