from pydantic import Field, Extra
from pydantic_settings import BaseSettings
import os
import pathlib

IN_DOCKER: bool = os.getenv('I_AM_IN_A_DOCKER_CONTAINER', False) == 'YES'

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
LOG_DIR: pathlib.Path = BASE_DIR / 'logs'


class EnvBase(BaseSettings):
    class Config:
        env_file = None if IN_DOCKER else '.env'
        extra = Extra.ignore


class AppSettings(EnvBase):
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        super().__init__()

    name: str = Field(alias='APP_NAME')
    debug: bool = Field(False, alias='DEBUG')
    jwt_token: str = Field(alias='JWT_TOKEN')
    auth_api_host: str = Field(alias='AUTH_API_HOST')
    auth_api_port: int = Field(alias='AUTH_API_PORT')
    notifications_api_host: str = Field(alias='NOTIFICATIONS_API_HOST')
    notifications_api_port: int = Field(alias='NOTIFICATIONS_API_PORT')

    @property
    def auth_api_url(self):
        return f'http://{self.auth_api_host}:{self.auth_api_port}/api/v1/users/'  # noqa:E501

    @property
    def notifications_api_url(self):
        return f'http://{self.publisher_host}:{self.publisher_port}/api/v1/send/important'  # noqa:E501


class JWTSettings(EnvBase):
    authjwt_algorithm: str = Field(alias='JWT_ALGORITHM')
    authjwt_public_key: str = Field(alias='JWT_PUBLIC_KEY')


class PostgresSettings(EnvBase):
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    db: str = Field(alias='POSTGRES_DB')
    search_path: str = 'billing'

    @property
    def get_uri(self):
        return 'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
            self.user,
            self.password,
            self.host,
            self.port,
            self.db
        )


class LoggingSettings(EnvBase):
    log_file: pathlib.Path = LOG_DIR / 'bot.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool


class Settings:
    app: AppSettings = AppSettings()
    jwt: JWTSettings = JWTSettings()
    logging: LoggingSettings = LoggingSettings()
    postgres: PostgresSettings = PostgresSettings()


settings = Settings()
