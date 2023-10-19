import pydantic
import pydantic_settings


class RabbitMQConfig(pydantic_settings.BaseSettings):
    host: str | None = pydantic.Field(..., alias="RABBITMQ_HOST")
    server_port: int | None = pydantic.Field(..., alias="RABBITMQ_SERVER_PORT")
    client_port: int | None = pydantic.Field(..., alias="RABBITMQ_CLIENT_PORT")
    user: str | None = pydantic.Field(..., alias="RABBITMQ_DEFAULT_USER")
    password: str | None = pydantic.Field(..., alias="RABBITMQ_DEFAULT_PASS")
