from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import fastapi

from publisher.src.api.v1.dtos.schedule import Task
from publisher.src.api.v1.dtos.send import (SendBodyPayloadDTO,
                                            SendQueryPriorityDTO)
from publisher.src.services.scheduler import Scheduler, get_scheduler_service

router = fastapi.APIRouter()


@router.post(
    "/task/{priority}",
    status_code=HTTPStatus.ACCEPTED
)
async def schedule(
        priority: SendQueryPriorityDTO,
        eta: datetime,
        payload: SendBodyPayloadDTO,
        days_of_week: list[int] | None = fastapi.Body(None),
        scheduler: Scheduler = fastapi.Depends(get_scheduler_service)
) -> UUID:
    if days_of_week is None:
        return await scheduler.schedule_once(priority, payload, eta)

    return await scheduler.schedule_periodic(priority, payload, eta,
                                             days_of_week)


@router.get(
    "/tasks",
    response_model=list[Task]
)
async def get_all(
        scheduler: Scheduler = fastapi.Depends(get_scheduler_service)
):
    return await scheduler.get_all_tasks()


@router.get(
    "/tasks/{task_id}",
    response_model=Task
)
async def get(
        task_id: UUID,
        scheduler: Scheduler = fastapi.Depends(get_scheduler_service)
):
    task = await scheduler.get_task(task_id)
    if task is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Задача с id={task_id} не найдена'
        )
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=HTTPStatus.ACCEPTED
)
async def delete(
        task_id: UUID,
        scheduler: Scheduler = fastapi.Depends(get_scheduler_service)
) -> None:
    if not await scheduler.remove_task(task_id):
        raise fastapi.HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Задача с id={task_id} не найдена'
        )
