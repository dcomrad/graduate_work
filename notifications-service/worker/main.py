import asyncio
import json
import logging
import os
from email.message import EmailMessage

import aio_pika
from dotenv import load_dotenv
from jinja2 import Template

from utils.dto import IdType, SendBodyPayloadDTO, Settings, TypeEnum
from utils.mapping import make_service_request
from utils.sender import send_email


def get_common_data(message: SendBodyPayloadDTO) -> {}:
    """
    Process a message received from the broker and replace common placeholders.

    Args:
        message (SendBodyPayloadDTO): An instance of SendBodyPayloadDTO containing message data.

    Returns:
        dict: A dictionary containing common data for this message.

    Raises:
        Exception: If an error occurs during message processing.
    """

    common_vars = {}
    common_vars["template"] = make_service_request(
        "template_id", message.template_id)

    for var_key, var_val in message.vars.items():
        key = var_key[:-3]  # storing without _id postfix, for proper rendering
        common_vars[key] = make_service_request(var_key, var_val)

    return common_vars


def get_specific_data(user_id: IdType) -> {}:
    """
    Retrieve specific user data based on the provided user ID.

    Args:
        user_id (IdType): A unique identifier for the user.

    Returns:
        dict: A dictionary containing user-specific data.

    Raises:
        SomeException: If an error occurs during data retrieval, this exception may be raised.
    """

    user_vars = {}
    user_vars["user"] = make_service_request("user_id", user_id)

    return user_vars


def process_message(message: SendBodyPayloadDTO, settings: Settings):
    """
    Enriches a message received from the broker with additional information using provided settings.

    Args:
        message (SendBodyPayloadDTO): An instance of SendBodyPayloadDTO containing message data.
        settings (Settings): An instance of Settings containing configuration options.

    Returns:
        None

    Raises:
        Exception: If an error occurs during message processing.
    """
    common_vars = get_common_data(message)
    template = Template(common_vars["template"]["text"])
    logging.debug(common_vars)
    if message.type == 'email':
        for user_id in message.recievers:
            user_vars = get_specific_data(user_id)
            all_vars = common_vars | user_vars
            email = EmailMessage()
            full_text = template.render(**all_vars)
            logging.debug(full_text)

            # Set the sender and recipient email addresses
            email.set_content(full_text)
            email["From"] = settings.smtp_from
            email["To"] = all_vars["user"]["email"]
            email["Subject"] = all_vars["template"]["subject"]

            try:
                send_email(email)
            except Exception as e:
                reason = f'{type(e).__name__}: {e}'
                logging.error(f'Something wrong. {reason}')
                continue

    else:
        logging.error(f'{message.type} not implemented yet ')
        raise NotImplementedError

    return None


async def consumer(rabbit_url, rabbit_queue_name):
    # Establish a connection to RabbitMQ server
    connection = await aio_pika.connect_robust(
        rabbit_url,  
    )

    # Create a channel
    channel = await connection.channel()

    # Declare a queue
    queue = await channel.declare_queue(rabbit_queue_name)

    async with queue.iterator() as queue_iter:
        async for queue_message in queue_iter:
            try:
                message_data = json.loads(queue_message.body.decode("utf-8"))
            except json.JSONDecodeError:
                print("Invalid JSON message:",
                      queue_message.body.decode("utf-8"))
                continue

            logging.info(message_data)

            message = SendBodyPayloadDTO(**message_data)
            smtp_settings = Settings()

            try:
                process_message(message, smtp_settings)
                # Acknowledge the message after successful processing
                await queue_message.ack()
            except Exception as e:
                reason = f'{type(e).__name__}: {e}'
                print(f'Something wrong. {reason}')
                # Reject the message (Nack) in case of an error to prevent reprocessing
                await queue_message.ack()

                continue


if __name__ == "__main__":

    load_dotenv()
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    rabbit_url = os.getenv("RABBIT_URL")
    rabbit_queue_name = os.getenv("RABBIT_QUEUE_NAME")
    loop = asyncio.get_event_loop()

    # Run the producer and consumer concurrently
    loop.run_until_complete(consumer(rabbit_url, rabbit_queue_name))

    # Close the loop
    loop.close()
