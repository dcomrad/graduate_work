from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import settings

Base = declarative_base()
Base.metadata.schema = settings.postgres.search_path


engine = create_async_engine(
    settings.postgres.get_uri,
    echo=settings.app.debug,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
