from src.crud.base import CRUDBase
from src.db_models.role_permission import RolePermission


class CRUDRolePermissions(CRUDBase):
    pass


role_permission_crud = CRUDRolePermissions(RolePermission)
