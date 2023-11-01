from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../infra/env.example/general', env_file_encoding='utf-8')

    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    db: str = Field(alias='POSTGRES_DB')
    search_path: str = Field(alias='POSTGRES_SEARCH_PATH')

    @property
    def get_uri(self):
        return 'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
            self.user,
            self.password,
            self.host,
            self.port,
            self.db
            )


config_postgres = PostgresSettings()
