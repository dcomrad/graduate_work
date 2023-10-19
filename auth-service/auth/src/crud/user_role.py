from src.crud.base import CRUDBase
from src.db_models.user_role import UserRole


class CRUDUserRole(CRUDBase):
    pass


user_role_crud = CRUDUserRole(UserRole)
