from pydantic import BaseModel


class Response(BaseModel):
    body: list[dict] | dict | None
    headers: dict
    status: int | None
