import random
import uuid
from http import HTTPStatus

import pytest

from functional.models.response import Response


async def test_get_all_subscriptions(
    make_http_request,
    get_subscriptions_url,
):
    response: Response = await make_http_request(
        'GET', f'{get_subscriptions_url}/'
    )

    assert isinstance(response.body, list)
    assert response.status == HTTPStatus.OK


async def test_get_subscription(
    make_http_request,
    get_subscriptions_url,
):
    all_subscriptions_response = await make_http_request(
        'GET', f'{get_subscriptions_url}/'
    )
    if not all_subscriptions_response.body:
        pytest.skip('No available subscriptions')
    subscription = random.choice(all_subscriptions_response.body)
    subscription_id = subscription.get('id')
    url = f'{get_subscriptions_url}/{subscription_id}'

    response: Response = await make_http_request('GET', url)

    assert isinstance(response.body, dict)
    assert response.body.get('id') == subscription_id
    assert response.status == HTTPStatus.OK


async def test_get_invalid_subscription(
    make_http_request,
    get_subscriptions_url,
):
    subscription_id = uuid.uuid4()
    url = f'{get_subscriptions_url}/{subscription_id}'

    response: Response = await make_http_request('GET', url)

    assert response.status == HTTPStatus.NOT_FOUND
