import abc
import functools
import http
import logging
import uuid

import aiohttp
import backoff
import fastapi
from src.config.config import settings
from src.core.logger import logger_factory
from src.core.utils import Response, make_http_request
from src.schemas import User


class BaseAPI(abc.ABC):
    SERVICE_REQUEST_ERROR = 'Ошибка при обращении к {service}-сервису'
    SERVICE_CONNECTION_ERROR = 'Ошибка при подключении к {service}-сервису'

    def __init__(
            self,
            api_name: str,
            api_url: str,
            jwt_token: str,
            logger: logging.Logger
    ):
        self.api_name = api_name
        self.api_url = api_url
        self.authorization_header = {'Authorization': f'Bearer {jwt_token}'}
        self.logger = logger

    @staticmethod
    async def _raise_connection_error(details: dict) -> None:
        self = details['args'][0]
        message = self.SERVICE_CONNECTION_ERROR.format(
            service=self.api_name
        )
        self.logger.error(message)
        raise fastapi.HTTPException(http.HTTPStatus.BAD_GATEWAY, message)

    def _check_response_status(
            self,
            response: Response,
            status_code: int
    ) -> None:
        if response.status_code != status_code:
            msg = self.SERVICE_REQUEST_ERROR.format(service=self.api_name)
            self.logger.error(
                f'{msg}: '
                f'status_code={response.status_code}, '
                f'response_body={response.body}'
            )
            raise fastapi.HTTPException(response.status_code, msg)


class AuthAPI(BaseAPI):
    def __init__(
            self,
            api_name: str,
            api_url: str,
            jwt_token: str,
            logger: logging.Logger = logger_factory(__name__)
    ):
        BaseAPI.__init__(**locals())

    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=3,
        on_giveup=BaseAPI._raise_connection_error
    )
    async def get_user(self, user_id: uuid.UUID) -> User:
        response = await make_http_request(
            'GET',
            f'{self.api_url}/users/{user_id}',
            headers={**self.authorization_header}
        )
        self._check_response_status(response, http.HTTPStatus.OK)
        return User.model_validate_json(response.body)

    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=3,
        on_giveup=BaseAPI._raise_connection_error
    )
    async def set_user_content_permission_rank(
            self,
            user_id: uuid.UUID,
            permission_rank: int
    ) -> None:
        response = await make_http_request(
            'PATCH',
            f'{self.api_url}/users/{user_id}/content_permission_rank/{permission_rank}',  # noqa:E501
            headers={**self.authorization_header}
        )
        self._check_response_status(response, http.HTTPStatus.NO_CONTENT)


class NotificationsAPI(BaseAPI):
    def __init__(
            self,
            api_name: str,
            api_url: str,
            jwt_token: str,
            logger: logging.Logger = logger_factory(__name__)
    ):
        BaseAPI.__init__(**locals())

    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=3,
        on_giveup=BaseAPI._raise_connection_error
    )
    async def send_email(
            self,
            receivers: list[uuid.UUID],
            template_id: uuid.UUID,
            template_vars: dict,
            priority: str = 'important'
    ):
        response = await make_http_request(
            'POST',
            f'{self.api_url}/send/{priority}',
            headers={**self.authorization_header},
            data={
                'type': 'email',
                'receivers': [str(receiver) for receiver in receivers],
                'template_id': str(template_id),
                'vars': template_vars
            }
        )
        self._check_response_status(response, http.HTTPStatus.ACCEPTED)


@functools.cache
def get_auth_api() -> AuthAPI:
    return AuthAPI(
        'auth',
        settings.app.auth_api_url,
        settings.app.jwt_token
    )


@functools.cache
def get_notifications_api() -> NotificationsAPI:
    return NotificationsAPI(
        'notifications',
        settings.app.notifications_api_url,
        settings.app.jwt_token
    )
