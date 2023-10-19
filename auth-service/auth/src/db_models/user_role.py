from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    role_id = Column(ForeignKey("role.id"), primary_key=True)

    _role = relationship("Role", lazy="joined")
