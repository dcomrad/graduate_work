# flake8: noqa: E501
import http

import orjson
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.exc import IntegrityError
from src.api.v1 import openapi
from src.core.logger import logger_factory
from src.db.postgres import AsyncSession, get_async_session
from src.managers import (get_payment_method_manager, get_subscription_manager,
                          get_transaction_manager)
from src.models.models import PaymentMethod, TransactionStatus
from src.providers.stripe import SignatureVerificationError

logger = logger_factory(__name__)

UNKNOWN_REQUEST = 'Неизвестный запрос: {request_body}'
VERIFYING_SIGNATURE_ERROR = 'Ошибка верификации подписи запроса: {details}'
UNHANDLED_EVENT = 'Необработанное событие {event_type}: {event}'
UNKNOWN_PAYMENT_METHOD = 'Неизвестный способ оплаты: {payment_method}'
UNKNOWN_REFUND = 'Неизвестный возврат средств: {refund}'

router = APIRouter(prefix='/webhooks/stripe')


@router.post(
    '/',
    status_code=http.HTTPStatus.OK,
    **openapi.webhooks.stripe_webhook.model_dump()
)
async def stripe_webhook(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
):
    # TODO: подумать над гарантией исполнения (ставить задачи в очередь задач после получниея события)
    # TODO: подумать над консистентностью (периодически запрашивать необработанные события и обрабатывать их)
    # TODO: разнести обработку событий в отдельные обработчики
    request_body = await request.body()
    try:
        event = orjson.loads(request_body)
    except orjson.JSONDecodeError:
        logger.error(UNKNOWN_REQUEST.format(request_body=request_body))
        return Response(status_code=http.HTTPStatus.BAD_REQUEST)
    except SignatureVerificationError as ex:
        logger.error(VERIFYING_SIGNATURE_ERROR.format(details=ex))
        return Response(status_code=http.HTTPStatus.BAD_REQUEST)

    match event['type']:
        #  Добавлен новый способ оплаты
        case 'payment_method.attached':
            payment_method = event['data']['object']
            user_id = payment_method['customer']

            if payment_method['type'] == PaymentMethod.CARD:
                card = payment_method['card']
                payload = {
                    'brand': card['brand'],
                    'expire': f'{card["exp_month"]}/{card["exp_year"]}',
                    'last4': card['last4']
                }
            else:
                logger.error(UNKNOWN_PAYMENT_METHOD.format(
                    payment_method=payment_method
                ))
                return Response(
                    status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
                )
            payment_method_manager = await get_payment_method_manager(user_id)

            try:
                await payment_method_manager.add(
                    session,
                    'stripe',
                    payment_method['id'],
                    payment_method['type'],
                    payload
                )
                # TODO: отправить письмо клиенту, что добавлен новый способ оплаты
            except IntegrityError as ex:
                if ex.orig.__cause__.__class__ == UniqueViolationError:
                    pass

        #  Способ оплаты удалён
        case 'payment_method.detached':
            payment_method = event['data']['object']
            user_id = event['data']['previous_attributes']['customer']

            payment_method_manager = await get_payment_method_manager(user_id)
            removed_payment_method = await payment_method_manager.remove(
                session, 'stripe', payment_method['id']
            )

            if removed_payment_method:
                # TODO: отправить письмо клиенту, что способ оплаты удалён
                pass

        #  Смена статуса платежа
        case 'payment_intent.processing' | 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            provider_transaction_id = payment_intent['id']
            transaction_id = payment_intent['metadata']['transaction_id']
            user_id = payment_intent['customer']

            if event['type'] == 'payment_intent.processing':
                status = TransactionStatus.PROCESSING
            else:
                status = TransactionStatus.FAILED

            transaction_manager = await get_transaction_manager(user_id)
            transaction = await transaction_manager.update(
                session,
                transaction_id,
                {
                    'provider_transaction_id': provider_transaction_id,
                    'status': status
                }
            )

            if transaction and status == TransactionStatus.FAILED:
                # TODO: отправить письмо клиенту, что платёж не прошёл
                pass

        #  Платёж успешно совершён
        case 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            provider_transaction_id = payment_intent['id']
            transaction_id = payment_intent['metadata']['transaction_id']
            user_id = payment_intent['customer']

            transaction_manager = await get_transaction_manager(user_id)

            transaction = await transaction_manager.update(
                session,
                transaction_id,
                {
                    'provider_transaction_id': provider_transaction_id,
                    'status': TransactionStatus.SUCCEEDED
                }
            )
            if transaction:
                subscription_manager = await get_subscription_manager(user_id)

                await subscription_manager.upgrade(
                    session, transaction[0].subscription_id
                )
                # TODO: отправить письмо клиенту, что платёж прошёл
                # TODO: Отправить письмо клиенту, что оформлена новая подписка

        #  Возврат средств успешно выполнен
        case 'charge.refunded':
            refund = event['data']['object']
            transaction_id = refund['metadata'].get('transaction_id')
            user_id = refund['customer']
            if transaction_id is None:
                logger.error(UNKNOWN_REFUND.format(refund=refund))
                return Response(
                    status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
                )

            transaction_manager = await get_transaction_manager(user_id)
            transaction = await transaction_manager.update(
                session,
                transaction_id,
                {'status': TransactionStatus.REFUNDED}
            )
            if transaction:
                subscription_manager = await get_subscription_manager(user_id)
                await subscription_manager.cancel(session)
                # TODO: отправить письмо клиенту, что осуществлён возврат средств

        case unhandled_event_type:
            logger.warning(UNHANDLED_EVENT.format(
                event_type=unhandled_event_type,
                event=event
            ))

    return Response(status_code=http.HTTPStatus.OK)
