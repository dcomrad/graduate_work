import functools
import logging

import aio_pika
import fastapi

from publisher.src.api.v1.dtos.send import (
    SendBodyPayloadDTO,
    SendQueryPriorityDTO,
    SendResponseDTO,
)
from publisher.src.core.config import Config, get_config
from publisher.src.core.logger import Logger, get_logger
from publisher.src.databases.rabbitmq import RabbitMQ, get_rabbitmq
from publisher.src.interfaces.repository import QueueRepository


class RabbitMQRepositoryException(Exception):
    pass


class RabbitMQRepository:
    def __init__(
        self,
        rabbitmq: RabbitMQ,
        config: Config,
        logger: Logger,
    ):
        self.rabbitmq = rabbitmq
        self.logger = logger
        self.config = config

    async def put_to_queue(
        self,
        priority: SendQueryPriorityDTO,
        payload: SendBodyPayloadDTO,
    ) -> None:
        channel = await self.rabbitmq.channel()

        try:
            queue = await channel.declare_queue(priority)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=bytes(payload.model_dump_json(), encoding="utf8")
                ),
                routing_key=queue.name,
            )
            self.logger.log_info(
                src=__name__, msg=f"published: queue{payload.model_dump_json()}"
            )
        except RabbitMQRepositoryException as e:
            self.logger.log_error(src=__name__, msg=e)
            raise
        finally:
            await channel.close()


def get_rabbitmq_repository(
    rabbitmq: aio_pika.Connection = fastapi.Depends(get_rabbitmq),
    config: Config = fastapi.Depends(get_config),
    logger: Logger = fastapi.Depends(get_logger),
) -> QueueRepository:
    return RabbitMQRepository(rabbitmq, config, logger)
