from typing import Any

import aiohttp
import pytest_asyncio
from aiohttp.client_exceptions import ContentTypeError
from pydantic import BaseModel


class Response(BaseModel):
    body: Any
    headers: dict
    status: int


@pytest_asyncio.fixture(scope="session")
async def aiohttp_client():
    """Возвращает клиент асинхронного http клиента."""
    async with aiohttp.ClientSession() as _client:
        yield _client


@pytest_asyncio.fixture(scope="session")
async def make_http_request(aiohttp_client: aiohttp.ClientSession):
    """Выполняет http запрос и возвращает его результат."""
    async def inner(method: str,
                    url: str,
                    headers: dict | None = None,
                    data: dict | None = None,
                    params: dict | None = None,
                    token: str | None = None):
        allowed_methods = ['GET', 'POST', 'DELETE', 'PATCH']
        if method.upper() not in allowed_methods:
            raise ValueError(f'Method should be one of the allowed: {allowed_methods}')

        if headers is None:
            headers = {}

        if token:
            headers['Authorization'] = f'Bearer {token}'

        headers['Content-Type'] = 'application/json'
        caller = getattr(aiohttp_client, method.lower())
        async with caller(url, params=params, headers=headers, json=data) as response:
            try:
                body = await response.json()
            except ContentTypeError:
                body = await response.text()
            return Response(body=body, headers=response.headers, status=response.status)

    return inner
