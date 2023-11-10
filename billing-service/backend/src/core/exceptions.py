from http import HTTPStatus

from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(HTTPStatus.NOT_FOUND, message)


class UnprocessableException(HTTPException):
    def __init__(self, message: str):
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, message)
