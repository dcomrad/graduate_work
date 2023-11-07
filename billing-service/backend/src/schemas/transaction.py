from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Extra
from src.schemas.payment_method import PaymentMethod
from src.schemas.subscription import Subscription


class Transaction(BaseModel):
    id: UUID  # noqa:VNE003
    subscription: Subscription
    payment_method: PaymentMethod
    amount: int
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        extra = Extra.ignore
