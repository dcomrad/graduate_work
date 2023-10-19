from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class UserService(Base):
    __tablename__ = "user_service"
    user_id = Column(ForeignKey("user.id"), primary_key=True)
    service_id = Column(ForeignKey("service.id"), primary_key=True)
    user_service_id = Column(String(50), nullable=False, primary_key=True)

    _service = relationship("Service", lazy="joined")
