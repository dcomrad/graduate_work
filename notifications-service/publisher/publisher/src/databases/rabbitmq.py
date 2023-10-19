import aio_pika

RabbitMQ = aio_pika.Connection

rabbitmq: RabbitMQ | None = None


async def get_rabbitmq():
    return rabbitmq
