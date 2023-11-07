# flake8: noqa: E501, VNE003
import enum

from sqlalchemy import (UUID, Boolean, Column, Date, DateTime, Enum,
                        ForeignKey, SmallInteger, String, Text, text)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from src.db.postgres import Base
from src.models.base_models import IDMixin


class Currency(str, enum.Enum):
    RUB = 'RUB'
    USD = 'USD'


class RecurringInterval(str, enum.Enum):
    MONTH = 'month'
    YEAR = 'year'


class TransactionStatus(str, enum.Enum):
    DRAFT = 'draft'
    PROCESSING = 'processing'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class PaymentMethod(str, enum.Enum):
    CARD = 'card'


class UserSubscription(Base, IDMixin):
    __tablename__ = "user_subscription"

    user_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("TIMEZONE('utc', now())"))
    expired_at = Column(Date, nullable=True)
    auto_renewal = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)

    subscription = relationship("Subscription", lazy="joined")


class Subscription(Base, IDMixin):
    __tablename__ = "subscription"

    name = Column(String(120), nullable=False)
    description = Column(Text(), nullable=True)
    is_active = Column(Boolean, nullable=False)
    price = Column(SmallInteger, nullable=False)  # в центах/копейках
    currency = Column(String(10), nullable=False, info={'choices': Currency}, default='RUB')
    recurring_interval = Column(String(10), nullable=False, info={'choices': RecurringInterval})
    recurring_interval_count = Column(SmallInteger, nullable=False)
    permission_rank = Column(SmallInteger, nullable=False)


class Provider(Base, IDMixin):
    __tablename__ = "provider"

    name = Column(String(50), nullable=False)


class UserPaymentMethod(Base, IDMixin):
    __tablename__ = "user_payment_method"

    type = Column(String(10), info={'choices': PaymentMethod}, default='card', nullable=False)
    payload = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    user_id = Column(UUID, nullable=False)
    provider_id = Column(UUID, ForeignKey("provider.id"), nullable=False)
    provider_payment_method_id = Column(String(64), nullable=False)


class Transaction(Base, IDMixin):
    __tablename__ = "transaction"

    provider_id = Column(UUID, ForeignKey("provider.id"), nullable=False)
    user_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    payment_method_id = Column(UUID, ForeignKey("user_payment_method.id"), nullable=False)
    provider_transaction_id = Column(String(64), nullable=True)
    amount = Column(SmallInteger, nullable=False)  # в центах/копейках
    currency = Column(String(10), nullable=False, info={'choices': Currency}, default='RUB')
    status = Column(String(40), nullable=False, info={'choices': TransactionStatus}, default='draft')
    created_at = Column(DateTime, nullable=False, server_default=text("TIMEZONE('utc', now())"))

    subscription = relationship("Subscription", lazy="joined")
    payment_method = relationship("UserPaymentMethod", lazy="joined")
