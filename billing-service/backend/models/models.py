from sqlalchemy import (Column, Enum, UUID, SmallInteger,
                        ForeignKey, DateTime, text,
                        Boolean, Date, String)
import enum
from backend.models.base_models import IDMixin
from backend.db.postgres import Base


class Currency(enum.Enum):
    RUB = "RUB"
    USD = "USD"


class UserSubscription(Base):
    __tablename__ = "user_subscription"
    user_id = Column(UUID, primary_key=True, nullable=False, unique=True)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    expired_at = Column(Date, nullable=True)
    auto_reneval = Column(Boolean, nullable=False)


class Subscription(Base, IDMixin):
    __tablename__ = "subscription"

    name = Column(String(120), nullable=False)
    price = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    period_days = Column(SmallInteger, nullable=False)
    permission_rang = Column(SmallInteger, default=0)


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
    currency = Column(Enum(Currency))
    product_id = Column(UUID, ForeignKey("subscription.id"))
    status = Column(String(40), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))
