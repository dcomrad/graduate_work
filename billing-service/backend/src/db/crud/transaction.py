from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import Transaction


class CRUDTransaction(CRUDBase):
    pass


transaction_crud = CRUDTransaction(Transaction, logger_factory(__name__))
