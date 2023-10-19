from os import path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv(path.join(path.dirname(__file__), '.env'))


class _PGData(BaseSettings):
    dbname: str = Field(env='POSTGRES_DB')
    pg_user: str = Field(env='POSTGRES_USER')
    password: str = Field(env='POSTGRES_PASSWORD')
    host: str = Field(env='POSTGRES_HOST')
    port: int = Field(env='POSTGRES_PORT')
    search_path: str = Field(env='POSTGRES_SEARCH_PATH')


class _ESData(BaseSettings):
    host: str = Field(env='ELASTIC_HOST')
    port: int = Field(env='ELASTIC_PORT')
    film_work_index: str = Field(env='ELASTIC_MOVIES_INDEX')
    genres_index: str = Field(env='ELASTIC_GENRES_INDEX')
    persons_index: str = Field(env='ELASTIC_PERSONS_INDEX')


class _RedisData(BaseSettings):
    host: str = Field(env='REDIS_HOST')
    port: int = Field(env='REDIS_PORT')


pg_data = _PGData().dict()
es_data = _ESData().dict()
redis_data = _RedisData().dict()
