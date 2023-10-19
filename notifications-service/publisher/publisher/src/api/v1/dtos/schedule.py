from pydantic import BaseModel


class Task(BaseModel):
    name: str
    total_run_count: int
    time: str
    day_of_week: list[str]
    priority: str
    payload: str
