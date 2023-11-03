import uuid

import requests.exceptions
from requests import Session

from utils.models import Response
from utils.urls import get_users_api_url

from config.base_settings import auth_settings
from utils.logger import logger


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
            if method.upper() not in self.ALLOWED_METHODS:
                raise ValueError(
                    f'Method should be one of the allowed: {self.ALLOWED_METHODS}')

            if headers is None:
                headers = {}

            if token:
                headers['Authorization'] = f'Bearer {token}'

            headers['Content-Type'] = 'application/json'
            caller = getattr(session, method.lower())
            with caller(
                url,
                data=data,
                json=json,
                params=params,
                headers=headers,
            ) as response:
                self.logger.debug('Response code: %s', response.status_code)
                try:
                    body = response.json()
                except requests.exceptions.RequestException as e:
                    body = response.text()
                return Response(
                    body=body,
                    headers=response.headers,
                    status=response.status_code,
                )
