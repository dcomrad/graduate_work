from logging import config as logging_config

from pydantic import BaseSettings, Field
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class ProjectSettings(BaseSettings):
    name: str = Field(env='PROJECT_NAME')
    default_page_size: int = Field(env='DEFAULT_PAGE_SIZE')
    max_page_size: int = Field(env='MAX_PAGE_SIZE')
    cache_expire_time_s: int = Field(env='CACHE_EXPIRE_TIME')


class JWTSettings(BaseSettings):
    authjwt_algorithm: str = Field(env='JWT_ALGORITHM')
    authjwt_public_key: str = Field(env='JWT_PUBLIC_KEY')


class ElasticSettings(BaseSettings):
    host: str = Field(env='ELASTIC_HOST')
    port: int = Field(env='ELASTIC_PORT')
    movies_index: str = Field(env='ELASTIC_MOVIES_INDEX')
    genres_index: str = Field(env='ELASTIC_GENRES_INDEX')
    persons_index: str = Field(env='ELASTIC_PERSONS_INDEX')


class RedisSettings(BaseSettings):
    host: str = Field(env='REDIS_HOST')
    port: int = Field(env='REDIS_PORT')


class Settings(BaseSettings):
    project: ProjectSettings = ProjectSettings()
    jwt: JWTSettings = JWTSettings()
    elastic: ElasticSettings = ElasticSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
