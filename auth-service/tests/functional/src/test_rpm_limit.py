from http import HTTPStatus

from tests.functional.testdata.test_data import User
from tests.functional.utils.generate_test_data import gtd


async def test_user_get(
        reg_and_login,
        make_http_request,
        get_user_api_url
):
    user_data = gtd(User(), 'full_name', 'login', 'password')
    user_data['email'] = 'email_limit_get@mail.ru'
    response = await reg_and_login(user_data)
    token = response.body['access']
    for req in range(100):
        response = await make_http_request('GET', get_user_api_url, token=token)
        assert response.status == HTTPStatus.OK
    response = await make_http_request('GET', get_user_api_url, token=token)
    assert response.status == HTTPStatus.TOO_MANY_REQUESTS
    assert response.body == {"error": "Rate limit exceeded: 5 per 1 minute"}
