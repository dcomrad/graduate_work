from fastapi import Request
from fastapi.responses import JSONResponse

from . import AuthJWTException


def authjwt_exception_handler(
        request: Request,
        exc: AuthJWTException
) -> JSONResponse:
    """Обработчик исключений, связанных с jwt токенами."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
