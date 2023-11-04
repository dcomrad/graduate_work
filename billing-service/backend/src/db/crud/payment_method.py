from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import PaymentMethod


class CRUDPaymentMethod(CRUDBase):
    pass


payment_method_crud = CRUDPaymentMethod(
    PaymentMethod, logger_factory(__name__)
)
