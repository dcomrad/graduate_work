from src.crud.base import CRUDBase
from src.db_models.user_service import UserService


class CRUDUserService(CRUDBase):
    pass


user_service_crud = CRUDUserService(UserService)
