from abc import ABC, abstractmethod
from base64 import b64encode
from functools import cache
from http import HTTPStatus

from fastapi import Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.exceptions import raise_error
from src.core.utils import make_http_request
from src.crud import service_crud, user_service_crud


class Client(BaseModel):
    id: str
    login: str
    full_name: str
    email: EmailStr
    service: dict


class OAuthBase(ABC):
    def __init__(
            self,
            auth_url: str,
            get_token_url: str,
            get_client_info_url: str
    ):
        self.auth_url = auth_url
        self.get_token_url = get_token_url
        self.get_client_info_url = get_client_info_url

    @abstractmethod
    async def get_auth_url(self) -> str:
        pass

    @abstractmethod
    async def get_client(self, code: str, session: AsyncSession) -> Client:
        pass

    @abstractmethod
    async def _get_tokens(self, code: str) -> dict:
        pass


class YandexOAuth(OAuthBase):
    def __init__(
            self,
            *args,
            client_id: str,
            client_secret: str,
    ):
        self.name = 'yandex'
        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__(*args)

    async def get_auth_url(self) -> str:
        return f'{self.auth_url}&client_id={self.client_id}'

    async def get_client(self, code: str, session: AsyncSession) -> Client:
        tokens = await self._get_tokens(code)

        response = await make_http_request(
            method='GET',
            url=self.get_client_info_url,
            headers={'Authorization': f'OAuth {tokens["access_token"]}'},
        )
        if response.status != HTTPStatus.OK:
            raise_error(HTTPStatus.UNPROCESSABLE_ENTITY, response.body)

        service = await service_crud.get_or_create_service(self.name, session)

        user_service = await user_service_crud.get_by_attribute(
            ['service_id', 'user_service_id'],
            [service.id, response.body['client_id']],
            session
        )

        return Client(
            service={'id': service.id, 'name': self.name,
                     'is_linked': bool(user_service),
                     'user_id': user_service.user_id if user_service else None},
            id=response.body['client_id'],
            login=response.body['login'],
            full_name=response.body['real_name'],
            email=response.body['default_email']
        )

    async def _get_tokens(self, code: str) -> dict:
        yandex = settings.oauth.yandex
        auth_header = b64encode(
            f'{yandex.client_id}:{yandex.client_secret}'.encode()
        ).decode()
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        body = {
            'grant_type': 'authorization_code',
            'code': code
        }
        response = await make_http_request(
            method='POST',
            url=self.get_token_url,
            headers=headers,
            params=None,
            body=body
        )
        if response.status != HTTPStatus.OK:
            raise_error(HTTPStatus.UNPROCESSABLE_ENTITY, response.body)

        return response.body


ALLOWED_SERVICES = {
    'yandex': YandexOAuth
}


@cache
def get_oauth_service(
        service_name: str = Query(..., description='Имя OAuth сервиса')
) -> OAuthBase:
    service = service_name.lower()
    return_class = ALLOWED_SERVICES.get(service)

    if return_class is None:
        services = ', '.join(ALLOWED_SERVICES)
        raise raise_error(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f'The application only supports the following services: {services}'
        )

    service_settings = getattr(settings.oauth, service)
    return return_class(
        service_settings.auth_url,
        service_settings.get_token_url,
        service_settings.get_client_info_url,
        client_id=service_settings.client_id,
        client_secret=service_settings.client_secret
    )
