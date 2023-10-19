import requests

ALLOWED_METHODS = ['GET', 'POST', 'DELETE', 'PATCH']


def make_http_request(
        method: str,
        url: str,
        headers: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
        token: str | None = None
) -> requests.Response:
    if method.upper() not in ALLOWED_METHODS:
        raise ValueError(
            f'Method should be one of the allowed: {ALLOWED_METHODS}')

    if headers is None:
        headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    headers['Content-Type'] = 'application/json'
    caller = getattr(requests, method.lower())
    return caller(url, params=params, headers=headers, json=data)
