import requests

from publisher.src.core.config import get_config
from publisher.src.databases._celery import get_celery

config = get_config()
celery = get_celery()


@celery.task
def send_notification(
    priority: str,
    payload: str,
):
    # TODO: вызывать SenderService.send напрямую (асинхронный метод)
    response = requests.post(
        f'http://{config.docker.app_host}:{config.app.port}/api/v1/send/{priority}',  # noqa:E501
        data=payload,
        headers={'Authorization': f'Bearer {config.app.jwt_token}'}
    )
    return response.status_code
