from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import Subscription


class CRUDSubscription(CRUDBase):
    pass


subscription_crud = CRUDSubscription(Subscription, logger_factory(__name__))
