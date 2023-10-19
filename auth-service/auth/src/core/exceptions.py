from http import HTTPStatus

from fastapi import HTTPException


def raise_error(status: HTTPStatus, message: str) -> None:
    """Базовый класс вызова исключения."""
    raise HTTPException(
        status_code=status,
        detail=message
    )


def raise_not_found(message: str) -> None:
    """Функция-обёртка для вызова исключения с ошибкой 404."""
    raise_error(HTTPStatus.NOT_FOUND, message)


def raise_already_exists(message: str) -> None:
    """Функция-обёртка для вызова исключения с ошибкой 422."""
    raise_error(HTTPStatus.UNPROCESSABLE_ENTITY, message)


def raise_forbidden(message: str) -> None:
    """Функция-обёртка для вызова исключения с ошибкой 403."""
    raise_error(HTTPStatus.FORBIDDEN, message)
