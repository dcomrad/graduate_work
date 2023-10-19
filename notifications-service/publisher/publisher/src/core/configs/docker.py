import pydantic
import pydantic_settings


class DockerConfig(pydantic_settings.BaseSettings):
    app_host: str = pydantic.Field(
        ...,
        alias="DOCKER_APP_HOST",
    )
    rabbitmq_host: str = pydantic.Field(
        ...,
        alias="DOCKER_RABBITMQ_HOST",
    )
