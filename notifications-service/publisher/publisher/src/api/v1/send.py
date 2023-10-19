import fastapi

from publisher.src.api.v1.dtos.send import (
    SendBodyPayloadDTO,
    SendQueryPriorityDTO,
    SendResponseDTO,
)
from publisher.src.interfaces.service import BrokerService
from publisher.src.services.sender import get_sender_service

router = fastapi.APIRouter()


@router.post("/{priority}")
async def send(
    priority: SendQueryPriorityDTO,
    payload: SendBodyPayloadDTO,
    service: BrokerService = fastapi.Depends(get_sender_service),
) -> SendResponseDTO:
    return await service.send(priority, payload)
