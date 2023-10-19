import asyncio
import logging
import os

import aio_pika
from dotenv import load_dotenv

from utils.dto import RabbitSettings, SendBodyPayloadDTO, TypeEnum


async def producer(rabbit_url, rabbit_queue_name):
    # Establish a connection to RabbitMQ server
    connection = await aio_pika.connect_robust(
        rabbit_url
    )

    # Create a channel
    channel = await connection.channel()

    # Declare a queue
    queue = await channel.declare_queue(rabbit_queue_name)

    try:
        while True:
            # Read user_id and template_id from the console
            user_id = input("Enter user_id: ")
            template_id = input("Enter template_id: ")

            if not user_id or not template_id:
                print("Both user_id and template_id are required.")
                continue

            # Create a message dictionary
            # message_data = {
            #     "user_id": user_id,
            #     "template_id": template_id,
            # }
            message_data = SendBodyPayloadDTO(
            template_id="9ab9df5e-c1a8-49fe-aca3-2462fdfc58e8",
            recievers=[
                    1,
                    2,
                    "e8106412-0cb9-422c-b5c3-0353a010f0a8",
                ],
                vars={"movie_id": "c05a3d39-622e-4da9-9a89-850b53ccea4d"},
                type=TypeEnum.email
            )

            # Serialize the message as JSON
            message_body = bytes(message_data.model_dump_json(), encoding="utf8")

            # Publish the message to the queue
            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body),
                routing_key=rabbit_queue_name,
            )
            logging.debug("Message sent.")

    except KeyboardInterrupt:
        pass

    # Close the channel and connection
    await channel.close()
    await connection.close()


if __name__ == "__main__":
    load_dotenv()
    rabbit_host = os.getenv("RABBIT_HOST")
    rabbit_port = os.getenv("RABBIT_PORT")
    rabbit_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbit_pass = os.getenv("RABBITMQ_DEFAULT_PASS")
    rabbit_url = f'amqp://{rabbit_user}:{rabbit_pass}@{rabbit_host}:{rabbit_port}/'
    rabbit_queue_name = os.getenv("RABBIT_QUEUE_NAME")
    loop = asyncio.get_event_loop()

    # Run the producer
    loop.run_until_complete(producer(rabbit_url, rabbit_queue_name))

    # Close the loop
    loop.close()
