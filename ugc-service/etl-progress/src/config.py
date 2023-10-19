from pydantic import BaseSettings, Field


class ProjectSettings(BaseSettings):
    refresh_period_s: int = Field(env='ETL_REFRESH_PERIOD')
    consumer_group: str = __name__


class KafkaSettings(BaseSettings):
    host: str = Field(env='KAFKA_HOST')
    port: int = Field(env='KAFKA_PORT')
    views_topic: str = Field(env='KAFKA_VIEWS_TOPIC')


class RedisSettings(BaseSettings):
    host: str = Field(env='REDIS_HOST')
    port: int = Field(env='REDIS_PORT')


class Settings(BaseSettings):
    project: ProjectSettings = ProjectSettings()
    kafka: KafkaSettings = KafkaSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
