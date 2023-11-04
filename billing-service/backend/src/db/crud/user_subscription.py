from src.db.crud.base import CRUDBase
from src.models.models import UserSubscription
from src.core.logger import logger_factory


class CRUDUserSubscription(CRUDBase):
    pass


user_subscription_crud = CRUDUserSubscription(
    UserSubscription, logger_factory(__name__)
)
