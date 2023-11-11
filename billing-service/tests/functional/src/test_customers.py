import random
import uuid
from http import HTTPStatus

import pytest

from functional.core.settings import tests_settings
from functional.models.response import Response


@pytest.mark.parametrize(
    'method, api_url, endpoint',
    [
        ('GET', 'get_customers_url', 'payment_methods'),
        ('GET', 'get_customers_url', 'subscription'),
        ('DELETE', 'get_customers_url', 'subscription'),
        ('GET', 'get_customers_url', 'transactions'),
    ],
)
async def test_unauthorized_customer(
    make_http_request,
    method,
    api_url,
    endpoint,
    request,
):
    url = f'{request.getfixturevalue(api_url)}/{endpoint}'

    response: Response = await make_http_request(method, url)

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_get_payment_methods(
    make_http_request,
    get_customers_url,
):
    url = f'{get_customers_url}/payment_methods/'

    response: Response = await make_http_request(
        'GET', url, token=tests_settings.user_token
    )

    assert isinstance(response.body, list)
    assert response.status == HTTPStatus.OK


async def test_default_payment_method(
    make_http_request,
    get_customers_url,
):
    payment_methods_url = f'{get_customers_url}/payment_methods/'
    payment_methods_response = await make_http_request(
        'GET', payment_methods_url, token=tests_settings.user_token
    )
    if not payment_methods_response.body:
        pytest.skip('No available payment method')
    payment_method = random.choice(payment_methods_response.body)
    payment_method_id = payment_method.get('id')
    url = f'{get_customers_url}/payment_methods/{payment_method_id}'

    response: Response = await make_http_request(
        'POST', url, token=tests_settings.user_token
    )

    assert response.status == HTTPStatus.NO_CONTENT


async def test_default_invalid_payment_method(
    make_http_request,
    get_customers_url,
):
    payment_method_id = uuid.uuid4()
    url = f'{get_customers_url}/payment_methods/{payment_method_id}'

    response: Response = await make_http_request(
        'POST', url, token=tests_settings.user_token
    )

    assert response.status == HTTPStatus.NOT_FOUND


async def test_get_subscription(
    make_http_request,
    get_customers_url,
):
    url = f'{get_customers_url}/subscription/'

    response: Response = await make_http_request(
        'GET', url, token=tests_settings.user_token
    )

    assert response.status == HTTPStatus.OK
    if not response.body:
        pytest.skip('No current subscription')
    assert isinstance(response.body, dict)


async def test_post_subscription(
    make_http_request,
    get_customers_url,
    get_subscriptions_url,
):
    payment_methods_url = f'{get_customers_url}/payment_methods/'
    payment_methods_response = await make_http_request(
        'GET', payment_methods_url, token=tests_settings.user_token
    )
    if not payment_methods_response.body:
        pytest.skip('No available payment method')
    payment_method = random.choice(payment_methods_response.body)
    payment_method_id = payment_method.get('id')

    all_subscriptions_response = await make_http_request(
        'GET', f'{get_subscriptions_url}/'
    )
    if not all_subscriptions_response.body:
        pytest.skip('No available subscriptions')
    subscription = random.choice(all_subscriptions_response.body)
    subscription_id = subscription.get('id')

    url = f'{get_customers_url}/subscription/{subscription_id}'

    response: Response = await make_http_request(
        'POST',
        url,
        token=tests_settings.user_token,
        params={'payment_method_id': payment_method_id},
    )

    assert response.status == HTTPStatus.NO_CONTENT


async def test_post_invalid_subscription(
    make_http_request,
    get_customers_url,
    get_subscriptions_url,
):
    payment_method_id = uuid.uuid4()
    subscription_id = uuid.uuid4()
    url = f'{get_customers_url}/subscription/{subscription_id}'

    response: Response = await make_http_request(
        'POST',
        url,
        token=tests_settings.user_token,
        params={'payment_method_id': f'{payment_method_id}'},
    )

    assert response.status == HTTPStatus.NOT_FOUND


async def test_get_transactions(
    make_http_request,
    get_customers_url,
):
    url = f'{get_customers_url}/transactions/'

    response: Response = await make_http_request(
        'GET', url, token=tests_settings.user_token
    )

    assert isinstance(response.body, list)
    assert response.status == HTTPStatus.OK
