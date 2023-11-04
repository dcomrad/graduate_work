from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import UserSubscription


class CRUDUserSubscription(CRUDBase):
    pass


user_subscription_crud = CRUDUserSubscription(
    UserSubscription, logger_factory(__name__)
)
