from http import HTTPStatus

import pytest
from asyncpg.exceptions import UniqueViolationError
from tests.functional.utils.jwt import get_perm_from_token, get_user_from_token


@pytest.mark.parametrize(
    'query_params, expected_response',
    [
        # Incorrect username
        (
            {'login': '', 'password': '123', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': '   ', 'password': '123', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'a', 'password': '123', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': None, 'password': '123', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        # Incorrect password
        (
            {'login': 'auth_user_1', 'password': '', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': '   ', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': '1', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': None, 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        # Incorrect full_name
        (
            {'login': 'auth_user_1', 'password': '123', 'full_name': '', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': '123', 'full_name': '   ', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': '123', 'full_name': 'I', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': None, 'full_name': None, 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        # Partial data
        (
            {'login': 'auth_user_1', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {'login': 'auth_user_1', 'password': '123', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        # Correct data
        (
            {'login': 'auth_user_1', 'password': '123', 'full_name': "Ivan Ivanov", 'email': 'email@mail.ru'},
            {'status': HTTPStatus.OK, 'login': 'auth_user_1'}
        ),
        # Correct data, but user already exists
        (
            {'login': 'auth_user_1', 'password': '123', 'full_name': "Ivan Ivanov", 'email': 'email@mail.ru'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
    ]
)
async def test_signup(
        reg_user,
        query_params,
        expected_response
):
    response = await reg_user(query_params)
    assert response.status == expected_response['status']
    if response.status == HTTPStatus.OK:
        assert response.body['login'] == expected_response['login']


@pytest.mark.parametrize(
    'query_params, expected_response',
    [
        # Incorrect login and password
        (
            {'login': 'incorrect', 'password': '123', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.NOT_FOUND}
        ),
        # Incorrect password
        (
            {'login': 'auth_user_2', 'password': 'incorrect', 'email': 'email@mail.ru'},
            {'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_incorrect_login(
        login,
        query_params,
        expected_response
):
    response = await login(query_params)
    assert response.status == expected_response['status']


async def test_login_superuser(
        login,
        create_user
):
    superuser_1 = 666
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    await create_user(id=superuser_1, login='auth_superuser_1',
                      hashed_password=hashed_password, is_superuser=True)

    response = await login({'login': 'auth_superuser_1', "password": '123'})

    assert get_user_from_token(response.body['access']) == superuser_1
    assert get_perm_from_token(response.body['access']) == '_all'


async def test_login_without_roles(
        reg_user,
        login
):
    await reg_user({"login": 'auth_user_2', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})

    response = await login({'login': 'auth_user_2', "password": '123'})

    assert response.status == HTTPStatus.OK
    assert not get_perm_from_token(response.body['access'])


async def test_login_with_roles(
        login,
        create_user,
        create_role,
        create_permission,
        create_user_role_relation,
        create_role_permission_relation
):
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    user_3 = 1001
    role_1, role_2 = 1001, 1002
    perm_1, perm_2, perm_3 = 1001, 1002, 1003

    # role_1: perm_1, perm_2
    # role_2: perm_2, perm_3
    await create_user(id=user_3, login='auth_user_3', hashed_password=hashed_password)
    await create_role(id=role_1, name='auth_role_1')
    await create_role(id=role_2, name='auth_role_2')
    await create_permission(id=perm_1, name='auth_perm_1')
    await create_permission(id=perm_2, name='auth_perm_2')
    await create_permission(id=perm_3, name='auth_perm_3')
    await create_user_role_relation(user_3, role_1)
    await create_user_role_relation(user_3, role_2)
    await create_role_permission_relation(role_1, perm_1)
    await create_role_permission_relation(role_1, perm_2)
    await create_role_permission_relation(role_2, perm_2)
    await create_role_permission_relation(role_2, perm_3)

    response = await login({'login': 'auth_user_3', "password": '123'})
    user_permissions = get_perm_from_token(response.body['access'])

    assert get_user_from_token(response.body['access']) == user_3
    assert sorted(user_permissions) == ['auth_perm_1', 'auth_perm_2', 'auth_perm_3']


async def test_logout_without_token(
        reg_user,
        login,
        logout
):
    await reg_user({"login": 'auth_user_4', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    await login({'login': 'auth_user_4', "password": '123'})

    response = await logout(access_token='')

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_logout_with_incorrect_token(
        reg_and_login,
        logout
):
    response = await reg_and_login({"login": 'auth_user_5', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_token = response.body['access']

    response = await logout(user_token + 'a')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_logout(
        reg_and_login,
        logout
):
    response = await reg_and_login({"login": 'auth_user_6', "password": '123', "full_name":'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_token = response.body['access']

    response = await logout(user_token)

    assert response.status == HTTPStatus.NO_CONTENT


async def test_logout_others_without_token(
        reg_and_login,
        logout_others
):
    await reg_and_login({"login": 'auth_user_7', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})

    response = await logout_others(access_token='')

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_logout_others_with_incorrect_token(
        reg_and_login,
        logout_others
):
    response = await reg_and_login({"login": 'auth_user_8', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_token = response.body['access']

    response = await logout_others(user_token + 'a')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_logout_others(
        reg_and_login,
        logout_others
):
    response = await reg_and_login({"login": 'auth_user_9', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_token = response.body['access']

    response = await logout_others(user_token)

    assert response.status == HTTPStatus.NO_CONTENT


async def test_refresh_without_token(
        reg_and_login,
        refresh
):
    await reg_and_login({"login": 'auth_user_10', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})

    response = await refresh(refresh_token='')

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_refresh_with_incorrect_token(
        reg_and_login,
        refresh
):
    response = await reg_and_login({"login": 'auth_user_11', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_token = response.body['refresh']

    response = await refresh(user_token + 'a')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_refresh(
        login,
        refresh,
        create_user,
        create_role,
        create_permission,
        create_user_role_relation,
        create_role_permission_relation
):
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    user_12 = 2001
    role_3 = 2001
    perm_4, perm_5 = 2001, 2002

    await create_user(id=user_12, login='auth_user_12', hashed_password=hashed_password)
    await create_role(id=role_3, name='auth_role_3')
    await create_permission(id=perm_4, name='auth_perm_4')
    await create_user_role_relation(user_12, role_3)
    await create_role_permission_relation(role_3, perm_4)

    response = await login({'login': 'auth_user_12', "password": '123'})
    user_permissions = get_perm_from_token(response.body['access'])
    user_refresh_token = response.body['refresh']

    assert get_user_from_token(response.body['access']) == user_12
    assert sorted(user_permissions) == ['auth_perm_4']

    await create_permission(id=perm_5, name='auth_perm_5')
    await create_role_permission_relation(role_3, perm_5)

    response = await refresh(user_refresh_token)
    user_permissions = get_perm_from_token(response.body['access'])

    assert get_user_from_token(response.body['access']) == user_12
    assert sorted(user_permissions) == ['auth_perm_4', 'auth_perm_5']


async def test_refresh_after_logout(
        reg_and_login,
        logout,
        refresh
):
    response = await reg_and_login({"login": 'auth_user_13', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})
    user_access_token = response.body['access']
    user_refresh_token = response.body['refresh']

    await logout(user_access_token)
    response = await refresh(user_refresh_token)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_refresh_after_logout_others(
        reg_user,
        login,
        logout_others,
        refresh
):
    await reg_user({'login': 'auth_user_14', 'password': '123', 'full_name': 'Ivan Ivanov', 'email': 'email@mail.ru'})

    #  вход с первого устройства
    response = await login({'login': 'auth_user_14', "password": '123'}, user_agent='1')
    user_access_token = response.body['access']
    user_refresh_token_1 = response.body['refresh']

    #  вход со второго устройства
    response = await login({'login': 'auth_user_14', "password": '123'}, user_agent='2')
    user_refresh_token_2 = response.body['refresh']

    #  проверка, что токены разных устройств различны
    assert user_refresh_token_1 != user_refresh_token_2

    await logout_others(user_access_token, '1')

    response = await refresh(user_refresh_token_2, '2')
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    response = await refresh(user_refresh_token_1, '1')
    assert response.status == HTTPStatus.OK


async def test_refresh_after_several_login(
        reg_user,
        login,
        refresh
):
    await reg_user({"login": 'auth_user_15', "password": '123', "full_name": 'Ivan Ivanov', 'email': 'email@mail.ru'})

    response = await login({'login': 'auth_user_15', "password": '123'})
    user_refresh_token_old = response.body['refresh']
    response = await login({'login': 'auth_user_15', "password": '123'})
    user_refresh_token_new = response.body['refresh']

    #  проверка, что токены разных устройств различны
    assert user_refresh_token_old != user_refresh_token_new

    response = await refresh(user_refresh_token_old)
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    response = await refresh(user_refresh_token_new)
    assert response.status == HTTPStatus.OK


async def test_user_permission_allowed(
        login,
        create_user,
        create_role,
        create_permission,
        create_user_role_relation,
        create_role_permission_relation,
        get_permissions_api_url,
        make_http_request,
        make_db_request
):
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    user_16 = 3001
    role_4 = 3001

    await create_user(id=user_16, login='auth_user_16', hashed_password=hashed_password)
    await create_role(id=role_4, name='auth_role_4')
    await create_user_role_relation(user_16, role_4)

    #  разрешение с именем "access_management" м.б. только одно в БД.
    #  проверяем наличие и берём id, если запись уже присутствует
    perm_5 = 3001
    permissions_get_all = 'access_management'
    try:
        await create_permission(id=perm_5, name=permissions_get_all)
    except UniqueViolationError:
        # роль с таки именем может быть одна, значит она была создана кем-то ранее
        sql = f"""SELECT * FROM "permission" WHERE "permission".name = '{permissions_get_all}'"""
        response = await make_db_request('FETCHONE', sql)
        perm_5 = response['id']
    await create_role_permission_relation(role_4, perm_5)

    response = await login({'login': 'auth_user_16', "password": '123'})
    user_access_token = response.body['access']

    url = get_permissions_api_url
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = await make_http_request('GET', url, headers, None)
    assert response.status == HTTPStatus.OK


async def test_superuser_permission_allowed(
        login,
        create_user,
        get_permissions_api_url,
        make_http_request
):
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    superuser_2 = 777

    await create_user(id=superuser_2, login='auth_superuser_2',
                      hashed_password=hashed_password, is_superuser=True)

    response = await login({'login': 'auth_superuser_2', "password": '123'})
    superuser_access_token = response.body['access']

    url = get_permissions_api_url
    headers = {'Authorization': f'Bearer {superuser_access_token}'}
    response = await make_http_request('GET', url, headers, None)
    assert response.status == HTTPStatus.OK


async def test_user_permission_denied(
        login,
        create_user,
        create_role,
        create_permission,
        create_user_role_relation,
        create_role_permission_relation,
        get_permissions_api_url,
        make_http_request
):
    hashed_password = 'sha256$4096$24326224313224503370696755543356434374504f75334b365853642e$bba234d9c9ac11841efdfd7b20df393ef35e8c9bf253733f257bcc4fc3259d12'
    user_17 = 4001
    await create_user(id=user_17, login='auth_user_17', hashed_password=hashed_password)

    # без разрешений
    response = await login({'login': 'auth_user_17', "password": '123'})
    user_access_token = response.body['access']

    url = get_permissions_api_url
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = await make_http_request('GET', url, headers, None)
    assert response.status == HTTPStatus.FORBIDDEN

    # с неверным разрешением
    role_5 = 4001
    perm_6 = 4001
    await create_role(id=role_5, name='auth_role_5')
    await create_permission(id=perm_6, name='auth_perm_6')
    await create_user_role_relation(user_17, role_5)
    await create_role_permission_relation(role_5, perm_6)

    response = await login({'login': 'auth_user_17', "password": '123'})
    user_access_token = response.body['access']

    url = get_permissions_api_url
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = await make_http_request('GET', url, headers, None)
    assert response.status == HTTPStatus.FORBIDDEN
