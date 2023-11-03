import uuid

import requests.exceptions
from requests import Session

from utils.models import Response
from utils.urls import get_users_api_url


class ApiHelper:
    def get_user_by_id(
        self,
        user_id: uuid.UUID,
        users_api_url: str = get_users_api_url(),
        token=None,
    ):
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
                try:
                    body = response.json()
                except requests.exceptions.RequestException:
                    body = response.text()
                return Response(
                    body=body,
                    headers=response.headers,
                    status=response.status_code,
                )
