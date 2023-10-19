from logging import config as logging_config

from pydantic import BaseSettings, Field
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class YandexOAuth(BaseSettings):
    client_id: str = Field(env='YANDEX_CLIENT_ID')
    client_secret: str = Field(env='YANDEX_CLIENT_SECRET')
    auth_url: str = Field(env='YANDEX_AUTH_URL')
    get_token_url: str = Field(env='YANDEX_TOKEN_URL')
    get_client_info_url: str = Field(env='YANDEX_CLIENT_INFO_URL')


class ProjectSettings(BaseSettings):
    name: str = Field(env='PROJECT_NAME')
    debug: bool = Field(False, env='DEBUG_MODE')
    default_page_size: int = Field(env='DEFAULT_PAGE_SIZE')
    rpm_limit: int = Field(env='RPM_LIMIT')


class OAuth(BaseSettings):
    yandex: YandexOAuth = YandexOAuth()


class JWTSettings(BaseSettings):
    authjwt_algorithm: str = Field(env='JWT_ALGORITHM')
    authjwt_public_key: str = Field(env='JWT_PUBLIC_KEY')
    authjwt_private_key: str = Field(env='JWT_PRIVATE_KEY')
    authjwt_access_token_expires:  int = Field(env='JWT_AT_EXPIRE')
    authjwt_refresh_token_expires: int = Field(env='JWT_RT_EXPIRE')


class PostgresSettings(BaseSettings):
    db_name: str = Field(env='POSTGRES_DB')
    host: str = Field(env='POSTGRES_HOST')
    port: int = Field(env='POSTGRES_PORT')
    user: str = Field(env='POSTGRES_USER')
    password: str = Field(env='POSTGRES_PASSWORD')
    search_path: str = Field(env='POSTGRES_SEARCH_PATH')


class RedisSettings(BaseSettings):
    host: str = Field(env='REDIS_HOST')
    port: int = Field(env='REDIS_PORT')


class Settings(BaseSettings):
    project: ProjectSettings = ProjectSettings()
    oauth: OAuth = OAuth()
    jwt: JWTSettings = JWTSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
