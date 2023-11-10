from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    body: Any
    headers: dict
    status: int
