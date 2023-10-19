import functools
import http

import fastapi
from publisher.src.api.v1.dtos.send import (
    SendBodyPayloadDTO,
    SendQueryPriorityDTO,
    SendResponseDTO,
)
from publisher.src.interfaces.repository import QueueRepository
from publisher.src.interfaces.service import BrokerService
from publisher.src.repositories.rabbitmq import (
    RabbitMQRepository,
    get_rabbitmq_repository,
)


class SenderServiceException(Exception):
    pass


class SenderService:
    def __init__(self, rabbitmq_repository: RabbitMQRepository) -> None:
        self.rabbitmq_repository = rabbitmq_repository

    async def send(
        self,
        priority: SendQueryPriorityDTO,
        payload: SendBodyPayloadDTO,
    ) -> SendResponseDTO:
        try:
            await self.rabbitmq_repository.put_to_queue(priority, payload)
            return SendResponseDTO(status=http.HTTPStatus.OK)
        except SenderServiceException:
            return SendResponseDTO(status=http.HTTPStatus.BAD_REQUEST)


@functools.lru_cache
def get_sender_service(
    rabbitmq_repository: QueueRepository = fastapi.Depends(get_rabbitmq_repository),
) -> BrokerService:
    return SenderService(rabbitmq_repository)
