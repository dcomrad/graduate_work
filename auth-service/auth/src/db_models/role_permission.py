from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id = Column(ForeignKey("role.id"), primary_key=True)
    permission_id = Column(ForeignKey("permission.id"), primary_key=True)

    _permission = relationship("Permission", lazy="joined")
