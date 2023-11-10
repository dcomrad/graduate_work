import uuid
from http import HTTPStatus

from functional.models.response import Response


async def test_unauthorized_refund(
    make_http_request,
    get_backoffice_url,
):
    transaction_id = uuid.uuid4()
    url = f'{get_backoffice_url}/refund/{transaction_id}'

    response: Response = await make_http_request('POST', url)

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_unauthorized_cancel(
    make_http_request,
    get_backoffice_url,
):
    user_subscription_id = uuid.uuid4()
    url = f'{get_backoffice_url}/subscription/{user_subscription_id}'

    response: Response = await make_http_request('DELETE', url)

    assert response.status == HTTPStatus.UNAUTHORIZED
