from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    dbname: str = Field(validation_alias='POSTGRES_DB', default='billing')
    user: str = Field(validation_alias='POSTGRES_USER', default='user')
    password: str = Field(
        validation_alias='POSTGRES_PASSWORD', default='qwert123'
    )
    host: str = Field(validation_alias='POSTGRES_HOST', default='localhost')
    port: int = Field(validation_alias='POSTGRES_PORT', default=5432)
    options: str = Field(
        validation_alias='POSTGRES_OPTIONS',
        default='',
    )


class DjangoSecuritySettings(BaseSettings):
    secret_key: str = Field(
        validation_alias='SECRET_KEY',
        default='default-django-secret-key',
    )
    allowed_hosts: str = Field(
        validation_alias='ALLOWED_HOSTS', default='127.0.0.1,*'
    )
    debug: bool = Field(validation_alias='DEBUG', default=False)


class AuthSettings(BaseSettings):
    host: str = Field(validation_alias='AUTH_HOST', default='51.250.6.208')
    port: int = Field(validation_alias='AUTH_PORT', default=5002)
    token: str = Field(validation_alias='AUTH_TOKEN', default='default-token')


class LoggerSettings(BaseSettings):
    loglevel: str = Field(validation_alias='LOGLEVEL', default='INFO')


postgres_settings = PostgresSettings()
django_security_settings = DjangoSecuritySettings()
auth_settings = AuthSettings()
logger_settings = LoggerSettings()
