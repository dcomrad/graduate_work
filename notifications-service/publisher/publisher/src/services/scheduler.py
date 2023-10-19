import uuid
from datetime import datetime, time
from functools import cache

import orjson
from celery import Celery
from celery.schedules import crontab
from pytz import timezone
from redbeat import RedBeatSchedulerEntry
from redis.asyncio import Redis

from publisher.src.api.v1.dtos.schedule import Task
from publisher.src.api.v1.dtos.send import (SendBodyPayloadDTO,
                                            SendQueryPriorityDTO)
from publisher.src.databases._celery import get_celery
from publisher.src.databases._redis import get_redis
from publisher.src.tasks.scheduler import send_notification

WEEKDAY = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    0: 'Воскресенье'
}


class Scheduler:
    def __init__(self, _redis: Redis, _celery: Celery):
        self.redis = _redis
        self.celery = _celery

    async def schedule_once(
            self,
            priority: SendQueryPriorityDTO,
            payload: SendBodyPayloadDTO,
            eta: datetime
    ) -> uuid.UUID:
        result = send_notification.apply_async(
            args=(priority, payload.model_dump_json()),
            eta=eta.replace(tzinfo=timezone(self.celery.conf.timezone))
        )
        return uuid.UUID(result.id)

    async def schedule_periodic(
            self,
            priority: SendQueryPriorityDTO,
            payload: SendBodyPayloadDTO,
            eta: datetime,
            days_of_week=list[int]
    ) -> uuid.UUID:
        task_id = uuid.uuid4()
        eta = eta.replace(tzinfo=timezone(self.celery.conf.timezone))
        entry = RedBeatSchedulerEntry(
            str(task_id),
            'publisher.src.tasks.scheduler.send_notification',
            crontab(
                hour=eta.hour,
                minute=eta.minute,
                day_of_week=days_of_week
            ),
            args=(priority, payload.model_dump_json()),
            app=self.celery
        )
        entry.save()
        return task_id

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        return await self._get_task_by_name(self._get_task_name(task_id))

    async def _get_task_by_name(self, name: str) -> Task | None:
        record = await self.redis.hgetall(name)

        if not record:
            return None

        total_run_count = orjson.loads(record[b'meta']).get('total_run_count', 0)  # noqa:E501
        task = orjson.loads((record[b'definition']))

        priority, payload = task['args']
        schedule = task['schedule']

        return Task(
            name=task['name'],
            total_run_count=total_run_count,
            time=time(
                hour=schedule['hour'], minute=schedule['minute']
            ).strftime('%H:%M'),
            day_of_week=[WEEKDAY[day] for day in schedule['day_of_week']],
            priority=priority,
            payload=payload
        )

    async def get_all_tasks(self) -> list[Task]:
        return [
            await self._get_task_by_name(key.decode())
            for key in await self.redis.keys('redbeat:*')
            if not key.startswith(b'redbeat::')
        ]

    async def remove_task(self, task_id: uuid.UUID) -> int:
        return await self.redis.delete(self._get_task_name(task_id))

    @staticmethod
    def _get_task_name(task_id: uuid.UUID) -> str:
        return f'redbeat:{str(task_id)}'


@cache
def get_scheduler_service() -> Scheduler:
    return Scheduler(get_redis(), get_celery())
