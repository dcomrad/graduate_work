from uuid import UUID

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str


class UserServiceCreate(BaseModel):
    user_id: UUID
    service_id: UUID
    user_service_id: str
