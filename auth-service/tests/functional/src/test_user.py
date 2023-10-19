from http import HTTPStatus
from random import randrange

import pytest
from tests.functional.testdata.test_data import User
from tests.functional.utils.generate_test_data import gtd


async def test_user_get(
        reg_and_login,
        make_http_request,
        get_user_api_url
):
    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'userget@mail.ru'
    response = await reg_and_login(user_data)
    response = await make_http_request('GET', get_user_api_url, token=response.body["access"])
    assert all((
        user_data['login'] == response.body['login'],
        user_data['full_name'] == response.body['full_name']
    ))


async def test_user_update(
        reg_and_login,
        make_http_request,
        get_user_api_url
):
    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'userupdate@mail.ru'
    response = await reg_and_login(user_data)
    response = await make_http_request('PATCH', get_user_api_url, token=response.body["access"],
                                       data={'full_name': 'updated_user'})
    assert response.body['full_name'] == 'updated_user'


async def test_change_login(
        reg_and_login,
        make_http_request,
        get_user_api_url
):
    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'chandelogin@mail.ru'
    response = await reg_and_login(user_data)

    new_user_login = gtd(User(), 'login')['login']
    response = await make_http_request('PATCH', f'{get_user_api_url}/change_login', token=response.body["access"],
                                       data={'login': new_user_login})
    assert all((
            response.body['full_name'] == user_data['full_name'],
            response.body['login'] == new_user_login
    ))


async def test_change_password(
        login,
        reg_and_login,
        make_http_request,
        get_user_api_url
):
    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'changepassword@mail.ru'
    response = await reg_and_login(user_data)
    response = await make_http_request('PATCH', f'{get_user_api_url}/change_password', token=response.body["access"],
                                       data={'password': 'new_pwd'})
    assert response.status == HTTPStatus.OK

    response = await login(user_data)
    assert response.status == 404

    user_data['password'] = 'new_pwd'
    response = await login(user_data)
    assert response.status == HTTPStatus.OK


async def test_access_history(
        reg_user,
        login,
        get_user_api_url,
        make_http_request
):
    await reg_user({"login": 'users_user_1', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'accesshistory@mail.ru'})

    await login({"login": 'users_user_1', "password": '123'}, user_agent='1')
    await login({"login": 'users_user_1', "password": '123'}, user_agent='2')
    response = await login({"login": 'users_user_1', "password": '123'}, user_agent='1')

    user_access_token = response.body['access']

    url = f'{get_user_api_url}/access_history'
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = await make_http_request('GET', url, headers, None)
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    assert response.body[1]['user_agent'] == '2'


@pytest.mark.parametrize(
    'query_params, expected_status',
    [
        (
                {'page_size': -1},
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
                {'page_size': 0},
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
                {'page_number': -1},
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
                {'page_number': 0},
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
    ]
)
async def test_access_history_pagination_error(
        reg_user,
        login,
        get_user_api_url,
        query_params,
        expected_status,
        make_http_request
):
    await reg_user({"login": 'users_user_2', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'accesshistorypag@mail.ru'})
    response = await login({"login": 'users_user_2', "password": '123'})
    user_access_token = response.body['access']

    url = f'{get_user_api_url}/access_history'
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = await make_http_request('GET', url, headers, None, query_params)

    assert response.status == expected_status


async def test_access_history_pagination(
        reg_user,
        login_several_times,
        get_user_api_url,
        make_http_request
):
    login_amount = randrange(5, 50)
    await reg_user({"login": 'users_user_3', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'achipa@mail.ru'})
    response = await login_several_times(login_amount, {"login": 'users_user_3', "password": '123'})
    user_access_token = response.body['access']

    url = f'{get_user_api_url}/access_history'
    headers = {'Authorization': f'Bearer {user_access_token}'}

    # 1
    query_params = {'page_size': 1, 'page_number': 1}
    response = await make_http_request('GET', url, headers, None, query_params)
    assert len(response.body) == 1

    # 2
    query_params = {'page_size': 1, 'page_number': login_amount}
    response = await make_http_request('GET', url, headers, None, query_params)
    assert len(response.body) == 1

    # 3
    query_params = {'page_size': 1, 'page_number': login_amount + 1}
    response = await make_http_request('GET', url, headers, None, query_params)
    assert len(response.body) == 0

    # 4
    query_params = {'page_size': 3, 'page_number': login_amount // 3 + 1}
    response = await make_http_request('GET', url, headers, None, query_params)
    assert len(response.body) == login_amount % 3

    # 5
    query_params = {'page_size': 4, 'page_number': login_amount // 4 + 1}
    response = await make_http_request('GET', url, headers, None, query_params)
    assert len(response.body) == login_amount % 4
