# flake8: noqa: E501
import datetime
import uuid

import fastapi
from src.core.logger import logger_factory
from src.db.crud import subscription_crud, user_subscription_crud
from src.db.postgres import AsyncSession
from src.jwt import AuthJWT
from src.managers.base import BaseManager
from src.managers.payment_method import get_payment_method_manager
from src.managers.transaction import get_transaction_manager
from src.models.models import RecurringInterval, Subscription, UserSubscription
from src.providers import get_provider_manager
from src.services.external import AuthAPI, get_auth_api

DAYS_IN_MONTH = 30
DAYS_IN_YEAR = 365


class SubscriptionManager(BaseManager):
    def __init__(self, auth_api: AuthAPI, *args):
        self.auth_api = auth_api
        super().__init__(*args)

    async def get_active(
            self,
            session: AsyncSession
    ) -> UserSubscription | None:
        self.logger.debug(
            f'Запрос активной подписки пользователя {self.user_id}'
        )

        return await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )

    async def subscribe(
            self,
            session: AsyncSession,
            subscription_id: uuid.UUID,
            payment_method_id: uuid.UUID | None = None
    ) -> None:
        """Запрос на смену подписки. Вызывается из эндпоинтов по запросам
        пользователей.

        Если у пользователя нет активной подписки:
        - создаём новую транзакцию и направляем запрос в платёжный провайдер на
        списание средств за подписку subscription_id.

        Если у пользователя есть активная подписка, значит возможны следующие
        варианты:
        - renew: подписываемся на эту же активную подписку, т.е. включаем
        автоматическое продление по истечении срока подписки;
        - upgrade (запрос на улучшение подписки): создаём новую транзакцию и
        направляем запрос в платёжный провайдер на списание доплаты за
        более дорогую подписку;
        - downgrade (запрос на ухудшение подписки): текущую подписку не
        трогаем, но указываем subscription_id в качестве подписки, на которую
        будет переведён пользователь после истечения текущей.

        Если не передан payment_method_id, используется способ оплаты,
        используемый пользователем по-умолчанию.
        """
        self.logger.debug(
            f'Запрос на смену подписки {subscription_id} пользователем '
            f'{self.user_id} со способом оплаты {payment_method_id}'
        )

        payment_method_manager = await get_payment_method_manager(self.user_id)
        if payment_method_id is None:
            default_payment_method = await payment_method_manager.get_default(session)
            if default_payment_method is None:
                self.logger.error(
                    f'У пользователя {self.user_id} нет способа оплаты '
                    f'по-умолчанию'
                )
                return

            payment_method = default_payment_method
        else:
            payment_method = await payment_method_manager.get(
                session, payment_method_id
            )
            if payment_method is None:
                self.logger.error(
                    f'Способа оплаты {payment_method_id} не существует'
                )
                return

        subscription = await subscription_crud.get(session, {'id': subscription_id})
        if subscription is None:
            self.logger.error(f'Подписки {subscription_id} не существует')
            return

        provider_manager = get_provider_manager(payment_method.provider.name)
        transaction_manager = await get_transaction_manager(self.user_id)

        user_subscription = await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )
        if user_subscription is None:
            # NEW SUBSCRIPTION
            transaction = await transaction_manager.get_or_create(
                session,
                {
                    'provider_id': payment_method.provider_id,
                    'subscription_id': subscription.id,
                    'payment_method_id': payment_method.id,
                    'amount': subscription.price,
                    'currency': subscription.currency
                }
            )

            await provider_manager.charge(
                str(self.user_id),
                str(payment_method.provider_payment_method_id),
                subscription.price,
                subscription.currency,
                subscription.to_dict(),
                str(transaction.id)
            )
            return

        if user_subscription.subscription_id == subscription_id:
            # RENEW SUBSCRIPTION
            await self.renew(session)
            return

        if subscription.price > user_subscription.subscription.price:
            # UPGRADE SUBSCRIPTION

            # рассчитываем размер доплаты
            paid = user_subscription.subscription.price
            unused_share = self._get_unused_share(user_subscription)
            amount = subscription.price - int(paid * unused_share)

            transaction = await transaction_manager.get_or_create(
                session,
                {
                    'provider_id': payment_method.provider_id,
                    'subscription_id': subscription.id,
                    'payment_method_id': payment_method.id,
                    'amount': amount,
                    'currency': subscription.currency
                }
            )
            return await provider_manager.charge(
                str(self.user_id),
                str(payment_method.provider_payment_method_id),
                amount,
                subscription.currency,
                subscription.to_dict(),
                str(transaction.id)
            )

        # DOWNGRADE SUBSCRIPTION
        await self.downgrade(session, subscription.id)

    async def unsubscribe(
            self,
            session: AsyncSession
    ) -> None:
        self.logger.debug(
            f'Запрос на отмену автопродления активной подписки '
            f'пользователя {self.user_id}'
        )

        user_subscription = await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )

        if user_subscription is None:
            self.logger.error(
                f'У пользователя {self.user_id} нет активной подписки'
            )
            return

        await user_subscription_crud.update(
            session,
            {'id': user_subscription.id},
            {'renew_to': None}
        )

    async def renew(
            self,
            session: AsyncSession
    ) -> None:
        self.logger.debug(
            f'Запрос на возобновление автопродления активной подписки '
            f'пользователя {self.user_id}'
        )

        user_subscription = await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )

        if user_subscription is None:
            self.logger.error(
                f'У пользователя {self.user_id} нет активной подписки'
            )
            return

        if user_subscription:
            await user_subscription_crud.update(
                session,
                {'id': user_subscription.id},
                {'renew_to': user_subscription.subscription.id}
            )

    async def upgrade(
            self,
            session: AsyncSession,
            to_subscription_id: uuid.UUID
    ) -> None:
        self.logger.debug(
            f'Запрос на новую подписку, повышение или продление активной '
            f'подписки на {to_subscription_id} у пользователя {self.user_id}'
        )

        user_subscription = await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )

        if (user_subscription and
                user_subscription.subscription.id == to_subscription_id):
            # Продление существующей подписки
            expired_at = self._get_new_expiration_date(
                user_subscription, user_subscription.subscription
            )
            await user_subscription_crud.update(
                session,
                {'id': user_subscription.id},
                {'expired_at': expired_at}
            )
            return

        # Переход на новую подписку
        if user_subscription:
            await user_subscription_crud.update(
                session,
                {'id': user_subscription.id},
                {'is_active': False, 'renew_to': None}
            )

        to_subscription = await subscription_crud.get(
            session, {'id': to_subscription_id}
        )
        expired_at = self._get_new_expiration_date(
            user_subscription, to_subscription
        )
        await user_subscription_crud.create(
            session,
            {
                'user_id': self.user_id,
                'subscription_id': to_subscription.id,
                'expired_at': expired_at,
                'renew_to': to_subscription.id
            }
        )

        # Обновляем пользователю права на доступ к контенту
        await self.auth_api.set_user_content_permission_rank(
            self.user_id,
            to_subscription.permission_rank
        )

    async def downgrade(
            self,
            session: AsyncSession,
            to_subscription_id: uuid.UUID
    ) -> None:
        self.logger.debug(
            f'Запрос на понижение активной подписки на {to_subscription_id} '
            f'у пользователя {self.user_id}'
        )

        await user_subscription_crud.update(
            session,
            {'user_id': self.user_id, 'is_active': True},
            {'renew_to': to_subscription_id}
        )

    async def cancel(
            self,
            session: AsyncSession
    ) -> None:
        """Вызывается в webhooks-эндпоинтах после получения сообщения от
        платёжных провайдеров об успешном возврате средств."""
        self.logger.debug(
            f'Запрос на отмену активной подписки у пользователя {self.user_id}'
        )
        active_subscription = await user_subscription_crud.get(
            session, {'user_id': self.user_id, 'is_active': True}
        )

        inactive_subscriptions = await user_subscription_crud.get_all(
            session,
            {'user_id': self.user_id, 'is_active': False},
            sort='created_at desc',
        )

        # Ищем неистёкшие неактивные подписки, на которые можно будет перейти
        # после отмены текущей
        possible_subscriptions = [
            subscription for subscription in inactive_subscriptions
            if (subscription.expired_at > datetime.date.today() and
                subscription.created_at < active_subscription.created_at)
        ]

        # Деактивируем текущую подписку
        await user_subscription_crud.update(
            session,
            {'id': active_subscription.id},
            {'is_active': False, 'renew_to': None}
        )

        if possible_subscriptions:
            # Активируем предыдущую подписку. Если у пользователя есть способ
            # оплаты по-умолчанию, включаем автопродление новой подписки
            new_subscription = possible_subscriptions[0]
            payment_method_manager = await get_payment_method_manager(self.user_id)
            default_payment_method = await payment_method_manager.get_default(session)
            renew_to = new_subscription.subscription.id if default_payment_method else None

            await user_subscription_crud.update(
                session,
                {'id': new_subscription.id},
                {'is_active': True, 'renew_to': renew_to}
            )

            # Меняем доступ к контенту в соответствии с уровнем новой подписки
            await self.auth_api.set_user_content_permission_rank(
                self.user_id, new_subscription.subscription.permission_rank
            )
        else:
            # Закрываем пользователю доступ к контенту
            await self.auth_api.set_user_content_permission_rank(self.user_id, 0)

    @staticmethod
    def _get_unused_share(
            user_subscription: UserSubscription
    ) -> float:
        # TODO: сделать корректный расчёт размера доплаты по формуле:
        #  <стоимость новой подписки> - <стоимость старой подписки> * <доля неизрасходованного срока>
        return 1.0

    @staticmethod
    def _get_new_expiration_date(
            user_subscription: UserSubscription | None,
            new_subscription: Subscription
    ) -> datetime.date:
        match new_subscription.recurring_interval:
            case RecurringInterval.MONTH:
                recurring_interval_days = DAYS_IN_MONTH * new_subscription.recurring_interval_count
            case RecurringInterval.YEAR:
                recurring_interval_days = DAYS_IN_YEAR * new_subscription.recurring_interval_count
            case _:
                raise ValueError(f'Неизвестный интервал подписки {new_subscription.recurring_interval}')

        start_from = user_subscription.created_at if user_subscription else datetime.date.today()

        return start_from + datetime.timedelta(days=recurring_interval_days)


async def get_subscription_manager_di(
        authorize: AuthJWT = fastapi.Depends(),
) -> SubscriptionManager:
    return SubscriptionManager(
        get_auth_api(),
        uuid.UUID(await authorize.get_jwt_subject()),
        logger_factory(__name__)
    )


async def get_subscription_manager(
        user_id: uuid.UUID | str
) -> SubscriptionManager:
    user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    return SubscriptionManager(
        get_auth_api(), user_id, logger_factory(__name__)
    )
