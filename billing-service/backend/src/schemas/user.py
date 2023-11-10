from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID  # noqa:VNE003
    email: str
    full_name: str
    content_permission_rank: int
