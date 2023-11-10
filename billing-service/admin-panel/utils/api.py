import uuid

import requests.exceptions
from requests import Session

from config.base_settings import auth_settings, billing_api_settings
from utils.logger import logger
from utils.models import Response
from utils.urls import (
    get_cancel_sub_api_url,
    get_refund_api_url,
    get_users_api_url,
)


class ApiHelper:
    ALLOWED_METHODS = ['GET', 'POST', 'DELETE', 'PATCH']

    def __init__(self):
        self.logger = logger

    def get_user_by_id(
        self,
        user_id: uuid.UUID,
        users_api_url: str = get_users_api_url(),
        token: str = auth_settings.token,
    ):
        self.logger.info('Requesting user %s', user_id)
        url = f'{users_api_url}/{user_id}'
        return self._make_http_request('GET', url, token=token)

    def refund_transaction(
        self,
        transaction_id: uuid.UUID,
        refund_api_url: str = get_refund_api_url(),
        token: str = billing_api_settings.token,
    ):
        self.logger.info('Refunding transaction %s', transaction_id)
        url = f'{refund_api_url}/{transaction_id}'
        return self._make_http_request('POST', url, token=token)

    def cancel_user_subscription(
        self,
        user_subscription_id: uuid.UUID,
        cancel_sub_api_url: str = get_cancel_sub_api_url(),
        token: str = billing_api_settings.token,
    ):
        self.logger.info(
            'Canceling user subscription %s', user_subscription_id
        )
        url = f'{cancel_sub_api_url}/{user_subscription_id}'
        return self._make_http_request('DELETE', url, token=token)

    def _make_http_request(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        token: str | None = None,
    ) -> Response:
        with Session() as session:
            self.logger.info('Making %s request to %s', method, url)
            if method.upper() not in self.ALLOWED_METHODS:
                raise ValueError(
                    'Method should be one of the allowed: '
                    f'{self.ALLOWED_METHODS}'
                )

            if headers is None:
                headers = {}

            if token:
                headers['Authorization'] = f'Bearer {token}'

            headers['Content-Type'] = 'application/json'
            caller = getattr(session, method.lower())
            try:
                with caller(
                    url,
                    data=data,
                    json=json,
                    params=params,
                    headers=headers,
                ) as response:
                    self.logger.debug(
                        'Response code: %s', response.status_code
                    )
                    try:
                        body = response.json()
                    except requests.exceptions.JSONDecodeError:
                        body = response.text
                    return Response(
                        body=body,
                        headers=response.headers,
                        status=response.status_code,
                    )
            except requests.exceptions.RequestException as e:
                self.logger.exception(e)
