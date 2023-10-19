from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from src.db.postgres import Base
from src.db_models.base_models import IDMixin


class Role(Base, IDMixin):
    __tablename__ = 'role'
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    @property
    def permissions(self):
        return [permission._permission for permission in self._permissions]

    _permissions = relationship('RolePermission', lazy="joined", cascade="all, delete")
