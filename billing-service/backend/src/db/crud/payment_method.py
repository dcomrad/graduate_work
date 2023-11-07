from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import UserPaymentMethod


class CRUDUserPaymentMethod(CRUDBase):
    pass


user_payment_method_crud = CRUDUserPaymentMethod(
    UserPaymentMethod, logger_factory(__name__)
)
