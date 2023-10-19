from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.v1.routers import v1_router
from src.core.config import settings
from src.db.redis import token_storage
from src.jwt import AuthJWT, AuthJWTException, authjwt_exception_handler
from src.request_limiter import limiter

app = FastAPI(
    title=settings.project.name,
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)
app.include_router(v1_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware('http')
async def check_X_headers(request: Request, call_next):
    if 'X-Request-Id' not in request.headers:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Отсутствует заголовок X-Request-Id'
        )
    return await call_next(request)


@app.on_event('shutdown')
async def shutdown():
    await token_storage.close()


@AuthJWT.load_config
def get_config():
    """Сервисная функция библиотеки fastapi-jwt-auth для загрузки настроек."""
    return settings.jwt


app.add_exception_handler(AuthJWTException, authjwt_exception_handler)
