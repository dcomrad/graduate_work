from src.crud.base import CRUDBase
from src.db_models.access_history import AccessHistory


class CRUDAccessHistory(CRUDBase):
    """Класс для выполнение CRUD операция над моделью AccessHistory."""
    pass


access_history_crud = CRUDAccessHistory(AccessHistory)
