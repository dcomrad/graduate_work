from datetime import date
from uuid import UUID

from pydantic import BaseModel


class Subscription(BaseModel):
    id: UUID  # noqa:VNE003
    name: str
    description: str
    is_active: bool
    price: int
    currency: str
    recurring_interval: str
    recurring_interval_count: int

    class Config:
        from_attributes = True


class UserSubscription(BaseModel):
    subscription_id: UUID
    name: str
    expired_at: date | None
    auto_renewal: bool
