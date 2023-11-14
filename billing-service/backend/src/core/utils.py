from typing import Any

import aiohttp
from pydantic import BaseModel
from src.core.logger import logger_factory

logger = logger_factory(__name__)

ALLOWED_METHODS = ['GET', 'POST', 'DELETE', 'PATCH']
WRONG_HTTP_METHOD = f'Method should be one of the allowed: {ALLOWED_METHODS}'


class Response(BaseModel):
    body: Any
    headers: dict
    status_code: int


async def make_http_request(
    method: str,
    url: str,
    headers: dict | None = None,
    data: dict | None = None,
    params: dict | None = None,
    token: str | None = None
) -> Response:
    if method.upper() not in ALLOWED_METHODS:
        raise ValueError(WRONG_HTTP_METHOD)

    if headers is None:
        headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    headers['Content-Type'] = 'application/json'
    async with aiohttp.ClientSession() as aiohttp_client:
        try:
            async with aiohttp_client.request(
                method.lower(), url, params=params, headers=headers, json=data
            ) as response:
                body = await response.text()
                return Response(
                    body=body,
                    headers=response.headers,
                    status_code=response.status
                )
        except aiohttp.ClientError as ex:
            logger.error(ex)
            raise
