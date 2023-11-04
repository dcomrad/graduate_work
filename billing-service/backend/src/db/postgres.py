from src.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
Base.metadata.schema = settings.postgres.search_path


engine = create_async_engine(
    settings.postgres.get_uri,
    echo=settings.app.debug,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    """Генерирует асинхронные сессии. Применяется в dependency injection в
    эндпоинтах FastAPI."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
