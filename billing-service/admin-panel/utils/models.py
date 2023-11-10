from pydantic import BaseModel


class Response(BaseModel):
    body: list[dict] | dict | str | None
    headers: dict
    status: int | None
