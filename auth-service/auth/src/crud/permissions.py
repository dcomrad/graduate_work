from src.crud.base import CRUDBase
from src.db_models.permission import Permission


class CRUDPermissions(CRUDBase):
    pass


permission_crud = CRUDPermissions(Permission)
