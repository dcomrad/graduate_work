# flake8: noqa: E501, VNE003
from sqlalchemy import UUID, Boolean, Column, Date, DateTime, ForeignKey, text
from src.postgres import Base


class UserSubscription(Base):
    __tablename__ = "user_subscription"

    id = Column(UUID, primary_key=True, unique=True, nullable=False)
    user_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("TIMEZONE('utc', now())"))
    expired_at = Column(Date, nullable=True)
    renew_to = Column(UUID, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
