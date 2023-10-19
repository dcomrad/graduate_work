from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str


class UserServiceCreate(BaseModel):
    user_id: int
    service_id: int
    user_service_id: str
