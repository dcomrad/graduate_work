import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR: Path = Path(__file__).parent.parent
LOG_DIR: Path = BASE_DIR / 'logs'


class AppSettings(BaseSettings):
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        super().__init__()

    debug: bool = Field(False, env='DEBUG')
    jwt_token: str = Field(env='JWT_TOKEN')
    auth_api_host: str = Field(alias='AUTH_API_HOST')
    auth_api_port: int = Field(alias='AUTH_API_PORT')
    publisher_host: str = Field(alias='PUBLISHER_HOST')
    publisher_port: int = Field(alias='PUBLISHER_PORT')

    @property
    def users_api_url(self):
        return f'http://{self.auth_api_host}:{self.auth_api_port}/api/v1/users/'  # noqa:E501

    def send_api_url(self, priority: str):
        return f'http://{self.publisher_host}:{self.publisher_port}/api/v1/send/{priority}'  # noqa:E501

    def schedule_api_url(self, priority: str):
        return f'http://{self.publisher_host}:{self.publisher_port}/api/v1/schedule/task/{priority}'  # noqa:E501


class LoggingSettings(BaseSettings):
    log_file: Path = LOG_DIR / 'admin-panel.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool = Field(False, env='DEBUG')


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
