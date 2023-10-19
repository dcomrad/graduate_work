from http import HTTPStatus

import pytest_asyncio
from tests.functional.testdata.test_data import (Role, User,
                                                 UserWithAccessPermissions)
from tests.functional.utils.generate_test_data import gtd


async def test_users_get_all(
        login,
        make_http_request,
        get_users_api_url,
        reg_user
):
    login_response = await login(UserWithAccessPermissions().dict())

    user_data_1 = gtd(User(), 'full_name', 'login', 'password')
    user_data_1['email'] = 'email@mail.ru'
    user_data_2 = gtd(User(), 'full_name', 'login', 'password')
    user_data_2['email'] = 'email2@mail.ru'

    response_1 = await reg_user(user_data_1)
    assert response_1.status == HTTPStatus.OK

    response_2 = await reg_user(user_data_2)
    assert response_2.status == HTTPStatus.OK

    response = await make_http_request('GET', get_users_api_url, token=login_response.body['access'])
    assert isinstance(response.body, list)

    number_users_found = 0
    for r in response.body:
        if r['full_name'] in (user_data_1['full_name'], user_data_2['full_name']):
            number_users_found += 1

    assert number_users_found == 2


async def test_get_user(
        login,
        make_http_request,
        get_users_api_url
):
    predefined_user = UserWithAccessPermissions()
    login_response = await login(predefined_user.dict())

    response = await make_http_request('GET', f'{get_users_api_url}/{predefined_user.id}',
                                       token=login_response.body['access'])
    assert response.body['full_name'] == 'test user with permissions'


async def test_update_user(
        login,
        make_http_request,
        get_users_api_url,
        reg_user
):
    login_response = await login(UserWithAccessPermissions().dict())

    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'email@mail.ru'
    user_response = await reg_user(user_data)

    response = await make_http_request('PATCH', f'{get_users_api_url}/{user_response.body["id"]}',
                                       token=login_response.body['access'],data={'full_name': 'updated_name'})
    assert response.body['full_name'] == 'updated_name'


async def test_delete_user_role(
        login,
        make_http_request,
        get_users_api_url,
        reg_user,
        make_role
):
    login_response = await login(UserWithAccessPermissions().dict())

    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'email@mail.ru'
    user_response = await reg_user(user_data)
    assert user_response.status == HTTPStatus.OK

    role_data = gtd(Role(), 'name', 'description')
    role_response = await make_role(role_data, login_response.body['access'])
    assert role_response.status == HTTPStatus.OK

    response = await make_http_request('PATCH', f'{get_users_api_url}/{user_response.body["id"]}',
                                       token=login_response.body['access'], data={'roles': [role_response.body]})
    assert response.status == HTTPStatus.OK

    response = await make_http_request('DELETE', f'{get_users_api_url}/{user_response.body["id"]}/remove_user_roles',
                                       token=login_response.body['access'], data=[role_response.body])
    assert response.status == HTTPStatus.OK


    response = await make_http_request('GET', f'{get_users_api_url}/{user_response.body["id"]}',
                                       token=login_response.body['access'])
    assert response.body['roles'] == []
