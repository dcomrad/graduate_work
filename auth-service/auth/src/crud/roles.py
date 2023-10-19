from src.crud.base import CRUDBase
from src.db_models.role import Role


class CRUDRoles(CRUDBase):
    pass


role_crud = CRUDRoles(Role)
