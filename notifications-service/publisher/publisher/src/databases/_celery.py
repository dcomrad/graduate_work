from celery import Celery

from publisher.src.core.config import get_config

redis_config = get_config().redis
redis_url = f'redis://{redis_config.host}:{redis_config.port}'

celery = Celery(
    'tasks',
    broker=redis_url,
    backend=redis_url,
    include=['publisher.src.tasks.scheduler']
)
celery.conf.timezone = 'UTC'


def get_celery():
    return celery
