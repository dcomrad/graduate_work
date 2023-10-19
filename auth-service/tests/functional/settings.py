from pydantic import BaseSettings, Field


class AuthSettings(BaseSettings):
    host: str = Field('127.0.0.1', env='SERVER_HOST')
    port: str = Field('80', env='SERVER_PORT')


class PostgresSettings(BaseSettings):
    db_name: str = Field('database', env='POSTGRES_DB')
    host: str = Field('127.0.0.1', env='POSTGRES_HOST')
    port: int = Field(5432, env='POSTGRES_PORT')
    user: str = Field('user', env='POSTGRES_USER')
    password: str = Field('password', env='POSTGRES_PASSWORD')
    search_path: str = Field('users', env='POSTGRES_SEARCH_PATH')


class TestSettings(BaseSettings):
    auth: AuthSettings = AuthSettings()
    postgres: PostgresSettings = PostgresSettings()


test_settings = TestSettings()
