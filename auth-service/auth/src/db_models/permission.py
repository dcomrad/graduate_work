from sqlalchemy import Column, String, Text
from src.db.postgres import Base
from src.db_models.base_models import IDMixin


class Permission(Base, IDMixin):
    __tablename__ = 'permission'
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
