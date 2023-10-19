from http import HTTPStatus
from typing import Any

from fastapi import HTTPException

NOT_FOUND_MSG = 'Not found'


def raise_404_if_none(item: Any) -> None:
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=NOT_FOUND_MSG)


def raise_402(detail: str) -> None:
    raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                        detail=detail)
