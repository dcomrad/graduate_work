from src.db.crud.base import CRUDBase
from src.models.models import PaymentMethod
from src.core.logger import logger_factory


class CRUDPaymentMethod(CRUDBase):
    pass


payment_method_crud = CRUDPaymentMethod(PaymentMethod, logger_factory(__name__))
