import asyncio
from time import sleep

from kafka import KafkaConsumer, errors
from redis.asyncio import ConnectionError, Redis
from src.config import settings
from src.utils import backoff, get_configured_logger

logger = get_configured_logger(__name__)


async def main(broker, progress_storage):
    logger.info('ETL connected to the sources')
    while True:
        current_progress = {}

        for messages in broker.poll().values():
            for message in messages:
                current_progress[message.key] = message.value

        for user_film, timestamp in current_progress.items():
            await progress_storage.set(user_film.decode(), timestamp.decode())

        sleep(settings.project.refresh_period_s)


@backoff(errors.NoBrokersAvailable)
def get_broker():
    return KafkaConsumer(
        settings.kafka.views_topic,
        bootstrap_servers=[f'{settings.kafka.host}:{settings.kafka.port}'],
        auto_offset_reset='earliest',
        group_id=settings.project.consumer_group,
    )


@backoff(ConnectionError)
def get_progress_storage():
    return Redis(host=settings.redis.host, port=settings.redis.port)


if __name__ == '__main__':
    logger.info('ETL started')
    asyncio.run(main(get_broker(), get_progress_storage()))
