from pydantic import BaseModel


class BaseOpenapi(BaseModel):
    """Класс, хранящий атрибуты, описывающие эндпоинты."""
    summary: str
    description: str
    response_description: str = 'Успешный ответ'
