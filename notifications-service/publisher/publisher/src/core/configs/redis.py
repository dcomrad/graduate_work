import pydantic
import pydantic_settings


class RedisConfig(pydantic_settings.BaseSettings):
    host: str | None = pydantic.Field(alias="REDIS_HOST")
    port: int | None = pydantic.Field(alias="REDIS_PORT")
