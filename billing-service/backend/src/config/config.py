# flake8: noqa: E501
import os
import pathlib

from pydantic import Extra, Field
from pydantic_settings import BaseSettings

IN_DOCKER: bool = os.getenv('I_AM_IN_A_DOCKER_CONTAINER', False) == 'YES'

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
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
        return f'http://{self.auth_api_host}:{self.auth_api_port}/api/v1'

    @property
    def notifications_api_url(self):
        return f'http://{self.notifications_api_host}:{self.notifications_api_port}/api/v1'


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


class StripeSettings(EnvBase):
    secret_key: str = Field(alias='STRIPE_SECRET_KEY')
    publishable_key: str = Field(alias='STRIPE_PUBLISHABLE_KEY')


class ServerSettings(EnvBase):
    host: str = Field(alias='SERVER_HOST')
    port: int = Field(alias='SERVER_PORT')


class LoggingSettings(EnvBase):
    log_file: pathlib.Path = LOG_DIR / 'billing.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool


class Settings:
    app: AppSettings = AppSettings()
    jwt: JWTSettings = JWTSettings()
    postgres: PostgresSettings = PostgresSettings()
    stripe: StripeSettings = StripeSettings()
    server: ServerSettings = ServerSettings()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
