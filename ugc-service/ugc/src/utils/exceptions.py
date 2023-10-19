from http import HTTPStatus

from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=message)


class AlreadyExistsException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=message)
