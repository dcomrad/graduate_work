from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from pydantic import HttpUrl
from src.api.v1 import openapi
from src.core.exceptions import NotFoundException
from src.core.logger import logger_factory
from src.db.crud import (transaction_crud, user_payment_method_crud,
                         user_subscription_crud)
from src.db.postgres import AsyncSession, get_async_session
from src.jwt import AuthJWT, login_required
from src.schemas import (HTMLForm, Transaction, UserPaymentMethod,
                         UserSubscription)

logger = logger_factory(__name__)

payment_methods_router = APIRouter(prefix='/payment_methods')
subscriptions_router = APIRouter(prefix='/subscription')
transactions_router = APIRouter(prefix='/transactions')


#####################################
#  СПОСОБЫ ОПЛАТЫ
#####################################

@payment_methods_router.get(
    '/',
    response_model=list[UserPaymentMethod],
    **openapi.customer.get_all_payment_methods.model_dump()
)
@login_required()
async def get_all_payment_methods(
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос всех способов оплаты пользователя {user_id}')

    payment_methods = await user_payment_method_crud.get_all(
        session, {'user_id': user_id}
    )

    return [
        UserPaymentMethod.model_validate(payment_method, from_attributes=True)
        for payment_method in payment_methods
    ]


@payment_methods_router.post(
    '/',
    response_model=HTMLForm,
    **openapi.customer.add_payment_method.model_dump()
)
@login_required()
async def add_payment_method(
        button_text: str = Query(
            ...,
            description=('Текст, который будет отображен на кнопке в '
                         'HTML-форме добавления способа оплаты')
        ),
        redirect_url: HttpUrl = Query(
            ...,
            description=('Ссылка для перенаправления после добавления способа '
                         'оплаты')
        ),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug('Запрос на добавление нового способа оплаты '
                 f'пользователю {user_id} ("{button_text}", "{redirect_url}")')

    # TODO: направить запрос в платёжный провайдер на добавление способа оплаты
    return '<from></form>'


@payment_methods_router.post(
    '/{payment_method_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.set_default_payment_method.model_dump()
)
@login_required()
async def set_default_payment_method(
        payment_method_id: UUID = Path(..., description='ID способа оплаты'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос на установку способа оплаты {payment_method_id} '
                 f'по-умолчанию для пользователя {user_id}')

    payment_method = await user_payment_method_crud.get(
        session, {'user_id': user_id, 'id': payment_method_id}
    )
    if payment_method is None:
        raise NotFoundException(f'Способ оплаты {payment_method_id} '
                                f'у пользователя {user_id} не найден')

    if payment_method.is_default:
        return

    default_payment_method = await user_payment_method_crud.get(
        session, {'user_id': user_id, 'is_default': True}
    )

    if default_payment_method:
        await user_payment_method_crud.update(
            session, {'id': default_payment_method.id}, {'is_default': False}
        )

    await user_payment_method_crud.update(
        session, {'id': payment_method.id}, {'is_default': True}
    )


@payment_methods_router.delete(
    '/{payment_method_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.remove_payment_method.model_dump()
)
@login_required()
async def remove_payment_method(
        payment_method_id: UUID = Path(..., description='ID способа оплаты'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос на удаление способа оплаты {payment_method_id} '
                 f'у пользователя {user_id}')

    payment_method = await user_payment_method_crud.get(
        session, {'user_id': user_id, 'id': payment_method_id}
    )
    if payment_method is None:
        raise NotFoundException(f'Способ оплаты {payment_method_id} не найден')

    # TODO: направить запрос в платёжный провайдер на удаление способа оплаты

#####################################
#  ПОДПИСКИ
#####################################


@subscriptions_router.get(
    '/',
    response_model=UserSubscription | None,
    **openapi.customer.get_subscription.model_dump()
)
@login_required()
async def get_subscription(
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос текущей подписки пользователя {user_id}')

    user_subscription = await user_subscription_crud.get(
        session, {'user_id': user_id, 'is_active': True}
    )
    if user_subscription is None:
        return None

    return UserSubscription(
        subscription_id=user_subscription.subscription.id,
        name=user_subscription.subscription.name,
        expired_at=user_subscription.expired_at,
        auto_renewal=user_subscription.auto_renewal
    )


@subscriptions_router.post(
    '/{subscription_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.subscribe.model_dump()
)
@login_required()
async def subscribe(
        subscription_id: UUID = Path(..., description='ID подписки'),
        payment_method_id: UUID = Query(..., description='ID способа оплаты'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос на добавление подписки {subscription_id} '
                 f'пользователем {user_id} '
                 f'со способом оплаты {payment_method_id}')


@subscriptions_router.delete(
    '/{subscription_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.unsubscribe.model_dump()
)
@login_required()
async def unsubscribe(
        subscription_id: UUID = Path(..., description='ID подписки'),
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос на отмену подписки {subscription_id} '
                 f'пользователем {user_id}')


#####################################
#  ТРАНЗАКЦИИ
#####################################


@transactions_router.get(
    '/',
    response_model=list[Transaction],
    **openapi.customer.get_transactions.model_dump()
)
@login_required()
async def get_transactions(
        session: AsyncSession = Depends(get_async_session),
        authorize: AuthJWT = Depends(),
):
    user_id = await authorize.get_jwt_subject()
    logger.debug(f'Запрос всех транзакций пользователя {user_id}')

    transactions = await transaction_crud.get_all(
        session,
        {'user_id': user_id},
        sort='created_at desc'
    )

    return [
        Transaction.model_validate(transaction, from_attributes=True)
        for transaction in transactions
    ]
