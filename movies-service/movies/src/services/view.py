from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field
from src.core.config import settings


class SortView(BaseModel):
    sort: Optional[str] = None


class PaginationView(BaseModel):
    size: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)


class ResponseView(SortView, PaginationView):
    """Класс, хранящий параметры обработки результата запроса, такие как:
    сортировка (поле и направление) и пагинация."""
    pass


def get_view_service(
        sort: Optional[str] = Query(
            None,
            description='Название поля и направление сортировки [-]field_name'
        ),
        page_size: int = Query(
            settings.project.default_page_size,
            ge=1, le=settings.project.max_page_size,
            description='Количество записей на странице'),
        page_number: int = Query(1, ge=1, description='Номер страницы')
) -> ResponseView:
    """Сервис для получения параметров сортировки и пагинации данных.
    :param sort: поле и направление сортировки выдачи ([-]field)
    :param page_size: количество элементов для отображения
    :param page_number: номер страницы для отображения
    """
    return ResponseView(sort=sort, size=page_size,
                        offset=(page_number - 1) * page_size)
