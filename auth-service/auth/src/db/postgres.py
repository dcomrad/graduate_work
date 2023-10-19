from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.config import settings
from src.db.base import DATABASE_URL_TEMPLATE

Base = declarative_base()
Base.metadata.schema = settings.postgres.search_path

sqlalchemy_url = DATABASE_URL_TEMPLATE.format(
    dialect='postgresql',
    driver='asyncpg',
    user=settings.postgres.user,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    db_name=settings.postgres.db_name
)

engine = create_async_engine(
    sqlalchemy_url,
    echo=settings.project.debug,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    """Генерирует асинхронные сессии. Применяется в dependency injection в
    эндпоинтах FastAPI."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
