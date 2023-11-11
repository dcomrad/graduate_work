# flake8: noqa: E501
import os
from pathlib import Path

from pydantic import Extra, Field
from pydantic_settings import BaseSettings

IN_DOCKER: bool = os.getenv('I_AM_IN_A_DOCKER_CONTAINER', False) == 'YES'

BASE_DIR: Path = Path(__file__).parent.parent.parent
LOG_DIR: Path = BASE_DIR / 'logs'


class EnvBase(BaseSettings):
    class Config:
        env_file = None if IN_DOCKER else '.env'
        extra = Extra.ignore


class AppSettings(EnvBase):
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        super().__init__()

    refresh_period_s: str = Field(alias='REFRESH_PERIOD_S')
    jwt_token: str = Field(alias='WORKER_JWT_TOKEN')
    auth_api_host: str = Field(alias='AUTH_API_HOST')
    auth_api_port: int = Field(alias='AUTH_API_PORT')
    billing_api_host: str = Field(alias='BILLING_API_HOST')
    billing_api_port: int = Field(alias='BILLING_API_PORT')

    @property
    def auth_api_url(self):
        return f'http://{self.auth_api_host}:{self.auth_api_port}/api/v1'

    @property
    def billing_api_url(self):
        return f'http://{self.billing_api_host}:{self.billing_api_port}/api/v1'


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
    log_file: Path = LOG_DIR / 'billing.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool


class Settings:
    app: AppSettings = AppSettings()
    postgres: PostgresSettings = PostgresSettings()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
