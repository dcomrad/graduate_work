from sqlalchemy import Column, String
from src.db.postgres import Base
from src.db_models.base_models import IDMixin


class Service(Base, IDMixin):
    """Модель истории входов пользователя."""
    __tablename__ = 'service'
    name = Column(String(50), nullable=False)
