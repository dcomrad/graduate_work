import datetime
import http

import orjson
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.exc import IntegrityError
from src.api.v1 import openapi
from src.core.logger import logger_factory
from src.db.crud import (provider_crud, transaction_crud,
                         user_payment_method_crud, user_subscription_crud)
from src.db.postgres import AsyncSession, get_async_session
from src.models.models import (PaymentMethod, RecurringInterval,
                               TransactionStatus)
from src.providers.stripe import SignatureVerificationError
from src.services.external import AuthAPI, get_auth_api

logger = logger_factory(__name__)

UNKNOWN_REQUEST = 'Неизвестный запрос: {request_body}'
VERIFYING_SIGNATURE_ERROR = 'Ошибка верификации подписи запроса: {details}'
DUPLICATE_EVENT = 'Дублирование события: {event}'
UNHANDLED_EVENT = 'Необработанное событие {event_type}: {event}'
UNKNOWN_PAYMENT_METHOD = 'Неизвестный способ оплаты: {payment_method}'

router = APIRouter(prefix='/webhooks/stripe')


@router.post(
    '',
    status_code=http.HTTPStatus.OK,
    **openapi.webhooks.stripe_webhook.model_dump()
)
async def stripe_webhook(
        request: Request,
        auth_api: AuthAPI = Depends(get_auth_api),
        session: AsyncSession = Depends(get_async_session)
):
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
        # TODO: вынести обработчики в отдельные функции
        # TODO: подумать над гарантией исполнения
        case 'payment_method.attached':
            payment_method = event['data']['object']

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
                return Response(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)  # noqa:E501

            stripe_provider = await provider_crud.get(
                session, {'name': 'stripe'}
            )
            user_id = payment_method['customer']
            user_payment_methods = await user_payment_method_crud.get_all(
                session, {'user_id': user_id}
            )
            try:
                await user_payment_method_crud.create(
                    session,
                    {
                        'type': payment_method['type'],
                        'payload': payload,
                        'is_default': len(user_payment_methods) == 0,
                        'user_id': user_id,
                        'provider_id': stripe_provider.id,
                        'provider_payment_method_id': payment_method['id']
                    }
                )
            except IntegrityError as ex:
                if ex.orig.__cause__.__class__ == UniqueViolationError:
                    logger.error(DUPLICATE_EVENT.format(event=event))
                    return Response(status_code=http.HTTPStatus.BAD_REQUEST)
                raise

        case 'payment_method.detached':
            payment_method = event['data']['object']
            deleted_payment_method = await user_payment_method_crud.delete(
                session,
                {'provider_payment_method_id': payment_method['id']}
            )
            if deleted_payment_method and deleted_payment_method[0].is_default:
                # Если удалённый способ оплаты использовался по-умолчанию,
                # назначаем первый способ из оставшихся способом по-умолчанию
                payment_methods = await user_payment_method_crud.get_all(
                    session,
                    {'user_id': deleted_payment_method[0].user_id}
                )
                if payment_methods:
                    await user_payment_method_crud.update(
                        session,
                        {'id': payment_methods[0].id},
                        {'is_default': True}
                    )

        case 'payment_intent.processing':
            payment_intent = event['data']['object']
            provider_transaction_id = payment_intent['id']
            transaction_id = payment_intent['metadata']['transaction_id']
            await transaction_crud.update(
                session,
                {'id': transaction_id},
                {
                    'provider_transaction_id': provider_transaction_id,
                    'status': TransactionStatus.PROCESSING
                }
            )

        case 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            provider_transaction_id = payment_intent['id']
            transaction_id = payment_intent['metadata']['transaction_id']
            transaction = await transaction_crud.update(
                session,
                {'id': transaction_id},
                {
                    'provider_transaction_id': provider_transaction_id,
                    'status': TransactionStatus.SUCCEEDED
                }
            )

            user_id = transaction[0].user_id
            subscription = transaction[0].subscription

            today = datetime.date.today()
            expired_at = None

            if subscription.recurring_interval == RecurringInterval.MONTH:
                month = (today.month + subscription.recurring_interval_count) % 12  # noqa: E501
                expired_at = today.replace(month=1 if month == 0 else month)
            elif subscription.recurring_interval == RecurringInterval.YEAR:
                expired_at = today.replace(
                    year=today.year + subscription.recurring_interval_count
                )

            await user_subscription_crud.create(
                session,
                {
                    'user_id': user_id,
                    'subscription_id': subscription.id,
                    'expired_at': expired_at,
                }
            )

            # Открываем пользователю доступ к контенту
            await auth_api.set_user_content_permission_rank(
                user_id,
                subscription.permission_rank
            )
            # TODO: Предусмотреть возможность модификации подписки
            # TODO: Отправить письмо клиенту, что подписка куплена

        case 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            provider_transaction_id = payment_intent['id']
            transaction_id = payment_intent['metadata']['transaction_id']
            await transaction_crud.update(
                session,
                {'id': transaction_id},
                {
                    'provider_transaction_id': provider_transaction_id,
                    'status': TransactionStatus.FAILED
                }
            )
            # TODO: отправить письмо клиенту, что платёж не прошёл

        case 'charge.refunded':
            transaction_id = event['data']['object']['metadata'].get('transaction_id')  # noqa:E501
            if transaction_id is None:
                logger.error(f'Неизвестный возврат средств Stripe: {event}')
                return

            transaction = await transaction_crud.update(
                session,
                {'id': transaction_id},
                {'status': TransactionStatus.REFUNDED}
            )
            user_id = transaction[0].user_id

            await user_subscription_crud.update(
                session,
                {'user_id': user_id, 'is_active': True},
                {'is_active': False, 'auto_renewal': False}
            )

            # Закрываем пользователю доступ к контенту
            await auth_api.set_user_content_permission_rank(user_id, 0)
            # TODO: Поискать другую неистёкшую подписку для перехода на неё (даунгрейд)
            # TODO: отправить письмо клиенту, что осуществлён возврат средств

        case unhandled_event_type:
            logger.warning(UNHANDLED_EVENT.format(
                event_type=unhandled_event_type,
                event=event
            ))
