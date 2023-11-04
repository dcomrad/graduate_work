from http import HTTPStatus
from fastapi import APIRouter, Depends, Path
from src.jwt import AuthJWT, login_required
from src.db.postgres import get_async_session, AsyncSession
from src.db.crud import transaction_crud, user_subscription_crud
from uuid import UUID
from src.core.exceptions import NotFoundException
from src.core.logger import logger_factory
from src.api.v1 import openapi

logger = logger_factory(__name__)

router = APIRouter(prefix='/backoffice')


@router.post(
    '/refund/{transaction_id}',
    status_code=HTTPStatus.ACCEPTED,
    **openapi.backoffice.refund.model_dump()
)
@login_required('backoffice_manager')
async def refund(
        transaction_id: UUID = Path(..., description='ID способа оплаты'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    logger.debug(f'Запрос на возмещение средств по транзакции {transaction_id}')

    transaction = await transaction_crud.get(session, {'id': transaction_id})
    if transaction is None:
        raise NotFoundException(f'Транзакция {transaction_id} не найдена')

    # TODO: направить запрос в платёжный провайдер на возмещение средств


@router.delete(
    '/subscription/{user_subscription_id}',
    status_code=HTTPStatus.ACCEPTED,
    **openapi.backoffice.cancel_subscription.model_dump()
)
@login_required('backoffice_manager')
async def cancel_subscription(
        user_subscription_id: UUID = Path(..., description='ID способа оплаты'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    logger.debug(f'Запрос на отмену подписки {user_subscription_id}')

    user_subscription = await user_subscription_crud.get(
        session, {'id': user_subscription_id}
    )
    if user_subscription is None:
        raise NotFoundException(f'Подписка {user_subscription_id} не найдена')

    await user_subscription_crud.update(
        session,
        {'id': user_subscription_id},
        {'auto_renewal': False}
    )
