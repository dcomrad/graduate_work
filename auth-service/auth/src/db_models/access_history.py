from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from src.db.postgres import Base
from src.db_models.base_models import IDMixin


def create_partition(target, connection, **kw) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "access_history_2023" PARTITION OF "access_history" FOR VALUES FROM ('01.01.2023') TO ('01.01.2024')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "access_history_2024" PARTITION OF "access_history" FOR VALUES FROM ('01.01.2024') TO ('01.01.2025')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "access_history_2025" PARTITION OF "access_history" FOR VALUES FROM ('01.01.2025') TO ('01.01.2026')"""
    )


class AccessHistory(Base, IDMixin):
    """Модель истории входов пользователя."""
    __tablename__ = 'access_history'
    __table_args__ = (
        UniqueConstraint('id', 'access_time'),
        {
            'postgresql_partition_by': 'RANGE (access_time)',
            'listeners': [('after_create', create_partition)],
        }
    )
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    access_time = Column(DateTime(timezone=True), nullable=False, primary_key=True, default=datetime.now)
    user_agent = Column(String(200), nullable=False)
