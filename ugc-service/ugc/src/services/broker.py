from functools import cache
from uuid import UUID

from aiokafka import AIOKafkaProducer
from src.core.config import settings
from src.services.base import AbstractBroker


class KafkaBroker(AbstractBroker):
    def __init__(self, host: str, port: int, topic: str):
        self.bootstrap_server = f'{host}:{port}'
        self.topic = topic
        super().__init__(None)

    async def init(self):
        # https://github.com/aio-libs/aiokafka/issues/689
        self.broker = AIOKafkaProducer(
            bootstrap_servers=[self.bootstrap_server]
        )
        await self.broker.start()

    async def send(self, user_id: int, film_id: UUID, timestamp: int):
        if self.broker is None:
            await self.init()

        await self.broker.send(
            topic=self.topic,
            key=f'{user_id}+{film_id}'.encode(),
            value=f'{timestamp}'.encode()
        )

    def __del__(self):
        self.broker.stop()


@cache
def get_broker() -> AbstractBroker:
    return KafkaBroker(
        settings.kafka.host, settings.kafka.port, settings.kafka.views_topic
    )
