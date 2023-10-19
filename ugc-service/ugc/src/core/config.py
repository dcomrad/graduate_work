from pydantic import BaseSettings, Field


class ProjectSettings(BaseSettings):
    name: str = Field(env='PROJECT_NAME')
    port: int = Field(env='UGC_PORT')
    default_page_size: int = Field(env='DEFAULT_PAGE_SIZE')
    like_score: int = 10
    dislike_score: int = 0


class JWTSettings(BaseSettings):
    authjwt_algorithm: str = Field(env='JWT_ALGORITHM')
    authjwt_public_key: str = Field(env='JWT_PUBLIC_KEY')


class KafkaSettings(BaseSettings):
    host: str = Field(env='KAFKA_HOST')
    port: int = Field(env='KAFKA_PORT')
    views_topic: str = Field(env='KAFKA_VIEWS_TOPIC')


class RedisSettings(BaseSettings):
    host: str = Field(env='REDIS_HOST')
    port: int = Field(env='REDIS_PORT')


class MongoSettings(BaseSettings):
    host: str = Field(env='MONGO_HOST')
    port: str = Field(env='MONGO_PORT')
    dbname: str = Field(env='MONGO_DBNAME')
    bookmarks_collection: str = Field(env='MONGO_BOOKMARKS_COLLECTION_NAME')
    movies_rating_collection: str = Field(env='MONGO_MOVIES_RATING_COLLECTION_NAME')  # noqa:E501
    reviews_collection: str = Field(env='MONGO_REVIEWS_COLLECTION_NAME')
    reviews_rating_collection: str = Field(env='MONGO_REVIEWS_RATING_COLLECTION_NAME')  # noqa:E501

    @property
    def connection_uri(self):
        return f'mongodb://{self.host}:{self.port}/'


class Settings(BaseSettings):
    project: ProjectSettings = ProjectSettings()
    jwt: JWTSettings = JWTSettings()
    kafka: KafkaSettings = KafkaSettings()
    redis: RedisSettings = RedisSettings()
    mongo: MongoSettings = MongoSettings()


settings = Settings()
