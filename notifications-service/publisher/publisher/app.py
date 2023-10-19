import aio_pika
import fastapi
from redis.asyncio import Redis

from publisher.src.api.v1 import schedule as api_v1_schedule
from publisher.src.api.v1 import send as api_v1_send
from publisher.src.core.config import Config
from publisher.src.core.logger import Logger
from publisher.src.databases import _redis, rabbitmq


class Container:
    def __init__(
        self,
    ) -> None:
        self.config = Config()
        self.logger = Logger()

    def create_app(
        self,
    ) -> fastapi.FastAPI:
        app = fastapi.FastAPI(
            title="Сервис нотификации",
            docs_url="/api/v1/openapi",
            openapi_url="/api/v1/openapi.json",
            default_response_class=fastapi.responses.ORJSONResponse,
        )

        app.include_router(
            api_v1_send.router,
            prefix="/api/v1/send",
            tags=["send"],
        )
        app.include_router(
            api_v1_schedule.router,
            prefix="/api/v1/schedule",
            tags=["schedule"],
        )

        @app.on_event("startup")
        async def startup():
            user = self.config.rabbitmq.user
            password = self.config.rabbitmq.password
            host = self.config.docker.rabbitmq_host
            port = self.config.rabbitmq.client_port

            rabbitmq.rabbitmq = await aio_pika.connect_robust(
                f"amqp://{user}:{password}@{host}:{port}"
            )
            self.logger.log_info(src=__name__, msg="Connected to rabbitmq")

            _redis.redis = Redis(
                host=self.config.redis.host, port=self.config.redis.port
            )
            self.logger.log_info(src=__name__, msg="Connected to redis")

        @app.on_event("shutdown")
        async def shutdown():
            await rabbitmq.rabbitmq.close()
            self.logger.log_info(src=__name__, msg="Disconnected from rabbitmq")
            await _redis.redis.close()
            self.logger.log_info(src=__name__, msg="Disconnected from redis")

        return app
