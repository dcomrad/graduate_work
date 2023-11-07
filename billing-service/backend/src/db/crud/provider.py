from src.core.logger import logger_factory
from src.db.crud.base import CRUDBase
from src.models.models import Provider


class CRUDProvider(CRUDBase):
    pass


provider_crud = CRUDProvider(Provider, logger_factory(__name__))
