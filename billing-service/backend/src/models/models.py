# flake8: noqa: E501, VNE003
from sqlalchemy import (UUID, Boolean, Column, Date, DateTime, ForeignKey,
                        SmallInteger, String, Text, text)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from src.db.postgres import Base
from src.models.base_models import IDMixin

CURRENCY = [
    ('RUB', 'Российский рубль'),
    ('USD', 'Доллар США'),
]

RECURRING_INTERVAL = [
    ('month', 'Месяц'),
    ('year', 'Год'),
]

STATUS = [
    ('draft', 'Черновик'),
    ('processing', 'В обработке'),
    ('succeeded ', 'Успешно'),
    ('failed', 'Неуспешно'),
]

PAYMENT_METHOD = [
    ('card', 'Банковская карта'),
]


class UserSubscription(Base, IDMixin):
    __tablename__ = "user_subscription"

    user_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    expired_at = Column(Date, nullable=True)
    auto_renewal = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)

    subscription = relationship("Subscription", lazy="joined")


class Subscription(Base, IDMixin):
    __tablename__ = "subscription"

    name = Column(String(120), nullable=False)
    description = Column(Text())
    is_active = Column(Boolean, nullable=False)
    price = Column(SmallInteger, nullable=False)
    currency = Column(String(10), info={'choices': CURRENCY}, default='RUB')
    recurring_interval = Column(String(10), info={'choices': RECURRING_INTERVAL})
    recurring_interval_count = Column(SmallInteger, nullable=False)
    permission_rank = Column(SmallInteger)


class Provider(Base, IDMixin):
    __tablename__ = "provider"

    name = Column(String(50), nullable=False)


class PaymentMethod(Base, IDMixin):
    __tablename__ = "payment_method"

    type = Column(String(10), info={'choices': PAYMENT_METHOD}, default='card')
    payload = Column(JSON)
    is_default = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID, nullable=False)
    provider_id = Column(UUID, ForeignKey("provider.id"), nullable=False)
    provider_payment_method_id = Column(String(64), nullable=False)


class Transaction(Base, IDMixin):
    __tablename__ = "transaction"

    provider_id = Column(UUID, ForeignKey("provider.id"), nullable=False)
    user_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, ForeignKey("subscription.id"), nullable=False)
    payment_method_id = Column(UUID, ForeignKey("payment_method.id"), nullable=False)
    provider_transaction_id = Column(String(64), nullable=False)
    amount = Column(SmallInteger, nullable=False)
    currency = Column(String(10), info={'choices': CURRENCY}, default='RUB')
    status = Column(String(40), info={'choices': STATUS}, default='draft')
    created_at = Column(DateTime, server_default=text("TIMEZONE('utc', now())"))

    subscription = relationship("Subscription", lazy="joined")
    payment_method = relationship("PaymentMethod", lazy="joined")
