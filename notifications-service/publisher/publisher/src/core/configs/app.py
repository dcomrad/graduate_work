import pydantic
import pydantic_settings


class AppConfig(pydantic_settings.BaseSettings):
    host: str | None = pydantic.Field(
        ...,
        alias="APP_HOST",
    )
    port: int | None = pydantic.Field(
        ...,
        alias="APP_PORT",
    )
    jwt_token: str = pydantic.Field(env='JWT_TOKEN')
