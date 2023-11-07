# flake8: noqa: VNE003
import uuid

from pydantic import BaseModel

HTMLForm = str


class Card(BaseModel):
    brand: str
    expire: str
    last4: str


class UserPaymentMethod(BaseModel):
    id: uuid.UUID
    type: str
    payload: Card
    is_default: bool
