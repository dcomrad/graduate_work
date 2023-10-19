from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.db_models.service import Service
from src.schemas.oauth import ServiceCreate


class CRUDService(CRUDBase):
    async def get_or_create_service(
            self,
            service_name: str,
            session: AsyncSession
    ):
        service = await self.get_by_attribute('name', service_name, session)
        if service is None:
            service = await service_crud.create(
                ServiceCreate(name=service_name),
                session
            )
        return service


service_crud = CRUDService(Service)
