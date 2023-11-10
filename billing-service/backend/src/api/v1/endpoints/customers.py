# flake8: noqa: E501
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from pydantic import HttpUrl
from src.api.v1 import openapi
from src.core.exceptions import NotFoundException, UnprocessableException
from src.core.logger import logger_factory
from src.db.crud import subscription_crud
from src.db.postgres import AsyncSession, get_async_session
from src.jwt import AuthJWT, login_required
from src.managers.payment_method import (PaymentMethodManager,
                                         get_payment_method_manager_di)
from src.managers.subscription import (SubscriptionManager,
                                       get_subscription_manager_di)
from src.managers.transaction import (TransactionManager,
                                      get_transaction_manager_di)
from src.providers import ProviderManager, get_provider_manager
from src.providers.base import HTMLForm
from src.schemas import Transaction, UserPaymentMethod, UserSubscription

logger = logger_factory(__name__)

payment_methods_router = APIRouter(prefix='/payment_methods')
subscriptions_router = APIRouter(prefix='/subscription')
transactions_router = APIRouter(prefix='/transactions')

SUBSCRIPTION_ID = 'ID подписки'
PAYMENT_METHOD_ID = 'ID способа оплаты'
BUTTON_TEXT = (
    'Текст, который будет отображен на кнопке в HTML-форме добавления способа '
    'оплаты'
)
REDIRECT_URL = 'Ссылка для перенаправления после добавления способа оплаты'
PAYMENT_METHOD_REMOVAL_FORBIDDEN = (
        'Невозможно удалить единственный способ оплаты при наличии активной '
        'подписки с автопродлением'
)
PAYMENT_METHOD_NOT_FOUND = 'Способ оплаты {payment_method} не найден'
SUBSCRIPTION_NOT_FOUND = 'Подписка {subscription} не найдена'

#####################################
#  СПОСОБЫ ОПЛАТЫ
#####################################


@payment_methods_router.get(
    '/',
    response_model=list[UserPaymentMethod],
    **openapi.customer.get_all_payment_methods.model_dump()
)
@login_required()
async def get_payment_methods(
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        payment_method_manager: PaymentMethodManager = Depends(get_payment_method_manager_di)
):
    payment_methods = await payment_method_manager.get_all(session)

    return [
        UserPaymentMethod.model_validate(payment_method)
        for payment_method in payment_methods
    ]


@payment_methods_router.post(
    '/',
    response_model=HTMLForm,
    **openapi.customer.add_payment_method.model_dump()
)
@login_required()
async def add_payment_method(
        button_text: str = Query(..., description=BUTTON_TEXT),
        redirect_url: HttpUrl = Query(..., description=REDIRECT_URL),
        authorize: AuthJWT = Depends(),  # noqa
        provider_manager: ProviderManager = Depends(get_provider_manager)
):
    return await provider_manager.add_payment_method(
        await authorize.get_jwt_subject(), button_text, redirect_url
    )


@payment_methods_router.post(
    '/{payment_method_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.set_default_payment_method.model_dump()
)
@login_required()
async def set_default_payment_method(
        payment_method_id: UUID = Path(..., description=PAYMENT_METHOD_ID),
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        payment_method_manager: PaymentMethodManager = Depends(get_payment_method_manager_di)
):
    payment_method = await payment_method_manager.get(
        session, payment_method_id
    )

    if payment_method is None:
        raise NotFoundException(PAYMENT_METHOD_NOT_FOUND.format(
            payment_method=payment_method_id
        ))

    await payment_method_manager.set_default(session, payment_method_id)


@payment_methods_router.delete(
    '/{payment_method_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.remove_payment_method.model_dump()
)
@login_required()
async def remove_payment_method(
        payment_method_id: UUID = Path(..., description=PAYMENT_METHOD_ID),
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        provider_manager: ProviderManager = Depends(get_provider_manager),
        payment_method_manager: PaymentMethodManager = Depends(get_payment_method_manager_di),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager_di)
):
    payment_method = await payment_method_manager.get(
        session, payment_method_id
    )

    if payment_method is None:
        raise NotFoundException(PAYMENT_METHOD_NOT_FOUND.format(
            payment_method=payment_method_id
        ))

    subscription = await subscription_manager.get_active(session)
    payment_methods = await payment_method_manager.get_all(session)

    if subscription and subscription.renew_to and len(payment_methods) == 1:
        raise UnprocessableException(PAYMENT_METHOD_REMOVAL_FORBIDDEN)

    await provider_manager.remove_payment_method(
        str(payment_method.user_id),
        str(payment_method.provider_payment_method_id)
    )

#####################################
#  ПОДПИСКИ
#####################################


@subscriptions_router.get(
    '/',
    response_model=UserSubscription | None,
    **openapi.customer.get_subscription.model_dump()
)
@login_required()
async def get_active_subscription(
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager_di)
):
    user_subscription = await subscription_manager.get_active(session)

    if user_subscription is None:
        return None

    return UserSubscription(
        subscription_id=user_subscription.subscription.id,
        name=user_subscription.subscription.name,
        expired_at=user_subscription.expired_at,
        renew_to=user_subscription.renew_to
    )


@subscriptions_router.post(
    '/{subscription_id}',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.subscribe.model_dump()
)
@login_required()
async def subscribe(
        authorize: AuthJWT = Depends(),  # noqa
        subscription_id: UUID = Path(..., description=SUBSCRIPTION_ID),
        payment_method_id: UUID = Query(..., description=PAYMENT_METHOD_ID),
        session: AsyncSession = Depends(get_async_session),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager_di),
        payment_method_manager: PaymentMethodManager = Depends(get_payment_method_manager_di),
):
    subscription = await subscription_crud.get(session, {'id': subscription_id})
    if subscription is None:
        raise NotFoundException(SUBSCRIPTION_NOT_FOUND.format(
            subscription=subscription_id
        ))

    payment_method = await payment_method_manager.get(session, payment_method_id)
    if payment_method is None:
        raise NotFoundException(PAYMENT_METHOD_NOT_FOUND.format(
            payment_method=payment_method_id
        ))

    await subscription_manager.subscribe(session, subscription_id, payment_method_id)


@subscriptions_router.delete(
    '/',
    status_code=HTTPStatus.NO_CONTENT,
    **openapi.customer.unsubscribe.model_dump()
)
@login_required()
async def unsubscribe(
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager_di)
):
    await subscription_manager.unsubscribe(session)


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
        authorize: AuthJWT = Depends(),  # noqa
        session: AsyncSession = Depends(get_async_session),
        transaction_manager: TransactionManager = Depends(get_transaction_manager_di)
):
    transactions = await transaction_manager.get_transactions(session)

    return [
        Transaction.model_validate(transaction)
        for transaction in transactions
    ]
