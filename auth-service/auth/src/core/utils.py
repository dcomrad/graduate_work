import binascii
import hashlib
from typing import Any

import aiohttp
import bcrypt
from aiohttp.client_exceptions import ContentTypeError
from fastapi import Request
from pydantic import BaseModel


def hash_password(password: str) -> str:
    """Хэширует пароль и возвращает строковое представление, готовое для записи
    в БД в следующем формате:
        algorithm$hashing_iterations$salt$hashed_password, где
        algorithm - применённый алгоритм хеширования,
        hashing_iterations - количество итераций хеширования,
        salt - использованная в хешировании 'соль' (hexadecimal repr),
        hashed_password - хеш пароля с указанными выше параметрами (hexadecimal repr).
    """
    algorithm = 'sha256'
    iterations = 4096
    salt = bcrypt.gensalt()
    hash = hashlib.pbkdf2_hmac(algorithm, password.encode(), salt, iterations)

    return f'{algorithm}${iterations}${salt.hex()}${hash.hex()}'


def check_password(provided_password: str, user_hashed_password: str) -> bool:
    """Проверяет соответствие полученного пароля хешу, находящемуся в БД."""
    if not user_hashed_password:
        return False

    algorithm, iterations, salt, hash = user_hashed_password.split('$')
    provided_hash = hashlib.pbkdf2_hmac(
        algorithm,
        provided_password.encode(),
        binascii.unhexlify(salt),
        int(iterations)
    )

    return hash == provided_hash.hex()


def get_user_agent(request: Request) -> str:
    """Возвращает название пользовательского приложения, с которого осуществлён
    зарос. Функция используется для dependency injection FastAPI."""
    return request.headers.get('user-agent', 'Unknown agent')


class Response(BaseModel):
    body: Any
    headers: dict
    status: int


async def make_http_request(
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        body: dict | None = None
):
    """Выполняет http запрос и возвращает его результат."""
    allowed_methods = ['GET', 'POST', 'DELETE', 'PATCH']
    if method.upper() not in allowed_methods:
        raise ValueError(f'Method should be one of the allowed: {allowed_methods}')

    async with aiohttp.ClientSession() as client:
        caller = getattr(client, method.lower())
        async with caller(url, params=params, headers=headers, data=body) as response:
            try:
                body = await response.json()
            except ContentTypeError:
                body = await response.text()
            return Response(body=body, headers=response.headers, status=response.status)
