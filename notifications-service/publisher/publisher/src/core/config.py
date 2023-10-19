import functools

import pydantic_settings

from publisher.src.core.configs import (
    AppConfig,
    DockerConfig,
    RabbitMQConfig,
    RedisConfig,
)


class Config(pydantic_settings.BaseSettings):
    app: AppConfig = AppConfig()
    rabbitmq: RabbitMQConfig = RabbitMQConfig()
    docker: DockerConfig = DockerConfig()
    redis: RedisConfig = RedisConfig()


@functools.lru_cache
def get_config():
    return Config()
