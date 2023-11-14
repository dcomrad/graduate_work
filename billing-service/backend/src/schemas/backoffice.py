import uuid

from pydantic import BaseModel


class Charge(BaseModel):
    user_id: uuid.UUID
    subscription_id: uuid.UUID
