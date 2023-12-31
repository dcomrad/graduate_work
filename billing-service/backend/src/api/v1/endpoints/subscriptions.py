from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.api.v1 import openapi
from src.core.exceptions import NotFoundException
from src.core.logger import logger_factory
from src.db.crud import subscription_crud
from src.db.postgres import AsyncSession, get_async_session
from src.schemas import Subscription

logger = logger_factory(__name__)
router = APIRouter(prefix='/subscriptions')


@router.get(
    '/',
    response_model=list[Subscription],
    **openapi.subscription.get_all.model_dump()
)
async def get_all(
        session: AsyncSession = Depends(get_async_session)
):
    return await subscription_crud.get_all(session)


@router.get(
    '/{subscription_id}',
    response_model=Subscription,
    **openapi.subscription.get.model_dump()
)
async def get(
        subscription_id: UUID = Path(..., description='ID подписки'),
        session: AsyncSession = Depends(get_async_session),
):
    subscription = await subscription_crud.get(
        session, {'id': subscription_id}
    )
    if subscription is None:
        msg = f'Подписка {subscription_id} не найдена'
        logger.error(msg)
        raise NotFoundException(msg)

    return subscription
