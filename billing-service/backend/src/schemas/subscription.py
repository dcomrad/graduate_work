from datetime import date
from uuid import UUID

from pydantic import BaseModel, field_validator


class Subscription(BaseModel):
    id: UUID  # noqa:VNE003
    name: str
    description: str
    is_active: bool
    price: float
    currency: str
    recurring_interval: str
    recurring_interval_count: int

    @field_validator('price')
    @classmethod
    def convert(cls, value: int) -> float:
        """Преобразовывает цену подписки из центов/копеек в доллары/рубли."""
        return round(value / 100, 2)

    class Config:
        from_attributes = True


class UserSubscription(BaseModel):
    subscription_id: UUID
    name: str
    expired_at: date | None
    auto_renewal: bool
