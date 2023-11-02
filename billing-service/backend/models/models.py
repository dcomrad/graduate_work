from sqlalchemy import (Column, UUID, SmallInteger,
                        ForeignKey, DateTime, text,
                        Boolean, Date, String)
from models.base_models import IDMixin
from db.postgres import Base


class UserSubscription(Base):
    __tablename__ = "user_subscription"
    user_id = Column(UUID, primary_key=True, nullable=False, unique=True)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    expired_at = Column(Date, nullable=True)
    auto_renewal = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)


class Subscription(Base, IDMixin):
    __tablename__ = "subscription"

    name = Column(String(120), nullable=False)
    price = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    recurring_interval = Column(String(10), nullable=False)
    recurring_interval_count = Column(SmallInteger, nullable=False)
    permission_rank = Column(SmallInteger, default=0)
    currency = Column(String(10), nullable=False, default="RUB")


class Provider(Base, IDMixin):
    __tablename__ = "provider"

    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))


class Transaction(Base, IDMixin):
    __tablename__ = "transaction"

    provider_id = Column(UUID, ForeignKey("provider.id"), nullable=False)
    idempotency_key = Column(UUID, nullable=False)
    user_id = Column(UUID, ForeignKey("user_subscription.user_id"))
    amount = Column(SmallInteger, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"))
    status = Column(String(40), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))
