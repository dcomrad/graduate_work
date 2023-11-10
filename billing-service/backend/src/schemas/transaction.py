from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator
from src.schemas.payment_method import UserPaymentMethod
from src.schemas.subscription import Subscription


class Transaction(BaseModel):
    id: UUID  # noqa:VNE003
    subscription: Subscription
    payment_method: UserPaymentMethod
    amount: float
    currency: str
    status: str
    created_at: datetime

    @field_validator('amount')
    @classmethod
    def convert(cls, value: int) -> float:
        """Преобразовывает сумму транзакции из центов/копеек в доллары/рубли"""
        return round(value / 100, 2)

    class Config:
        from_attributes = True
