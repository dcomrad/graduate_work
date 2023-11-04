from uuid import UUID
from pydantic import BaseModel, Extra
from datetime import datetime
from src.schemas.subscription import Subscription
from src.schemas.payment_method import PaymentMethod


class Transaction(BaseModel):
    id: UUID
    subscription: Subscription
    payment_method: PaymentMethod
    amount: int
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        extra = Extra.ignore
