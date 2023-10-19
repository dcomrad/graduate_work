from elasticsearch import AsyncElasticsearch as Elasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from src.api.v1.routers import v1_router
from src.core.config import settings
from src.db import elastic, redis
from src.jwt import AuthJWT, AuthJWTException, authjwt_exception_handler

app = FastAPI(
    title=settings.project.name,
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(v1_router)


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    redis.cache.set_storage_instance(redis.RedisCacheStorage())
    elastic.es = Elasticsearch(
        hosts=[f'{settings.elastic.host}:{settings.elastic.port}']
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@AuthJWT.load_config
def get_config():
    """Сервисная функция библиотеки fastapi-jwt-auth для загрузки настроек."""
    return settings.jwt


app.add_exception_handler(AuthJWTException, authjwt_exception_handler)
