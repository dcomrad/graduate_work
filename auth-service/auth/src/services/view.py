from fastapi import Query
from pydantic import BaseModel, Field
from src.core.config import settings


class PaginationView(BaseModel):
    """Класс, хранящий параметры пагинации из запроса."""
    size: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)


def get_view_service(
        page_size: int = Query(
            settings.project.default_page_size,
            ge=1, description='Количество записей на странице'),
        page_number: int = Query(1, ge=1, description='Номер страницы')
) -> PaginationView:
    """Сервис для получения параметров пагинации данных.
    :param page_size: количество элементов для отображения
    :param page_number: номер страницы для отображения
    """
    return PaginationView(size=page_size, offset=(page_number - 1) * page_size)
