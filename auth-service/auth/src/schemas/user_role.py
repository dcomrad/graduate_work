from uuid import UUID

from pydantic import BaseModel


class UserRole(BaseModel):
    user_id: UUID
    role_id: UUID
