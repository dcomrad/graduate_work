import uuid

import fastapi
from src.core.logger import logger_factory
from src.db.crud import provider_crud, user_payment_method_crud
from src.db.postgres import AsyncSession
from src.jwt import AuthJWT
from src.managers.base import BaseManager
from src.models.models import PaymentMethod, UserPaymentMethod


class PaymentMethodManager(BaseManager):
    async def get(
            self,
            session: AsyncSession,
            payment_method_id: uuid.UUID
    ) -> UserPaymentMethod | None:
        self.logger.debug(
            f'Запрос способа оплаты {payment_method_id} пользователя '
            f'{self.user_id}'
        )

        return await user_payment_method_crud.get(
            session,
            {
                'user_id': self.user_id,
                'id': payment_method_id,
                'is_active': True
            }
        )

    async def get_all(
            self,
            session: AsyncSession
    ) -> list[UserPaymentMethod]:
        self.logger.debug(
            f'Запрос всех способов оплаты пользователя {self.user_id}'
        )

        return await user_payment_method_crud.get_all(
            session,
            {'user_id': self.user_id, 'is_active': True},
            sort='created_at desc'
        )

    async def get_default(
            self,
            session: AsyncSession
    ) -> UserPaymentMethod | None:
        self.logger.debug(
            f'Запрос способа оплаты по-умолчанию пользователя {self.user_id}'
        )

        return await user_payment_method_crud.get(
            session,
            {'user_id': self.user_id, 'is_active': True, 'is_default': True}
        )

    async def set_default(
            self,
            session: AsyncSession,
            payment_method_id: uuid.UUID
    ) -> None:
        self.logger.debug(
            f'Запрос на установку способа оплаты {payment_method_id} '
            f'по-умолчанию для пользователя {self.user_id}'
        )

        payment_method = await user_payment_method_crud.get(
            session,
            {
                'user_id': self.user_id,
                'id': payment_method_id,
                'is_active': True
            }
        )
        if payment_method is None:
            self.logger.error(
                f'Способа оплаты {payment_method_id} не существует или он не '
                f'принадлежит пользователю {self.user_id}'
            )
            return

        if payment_method.is_default:
            return

        default_payment_method = await user_payment_method_crud.get(
            session,
            {'user_id': self.user_id, 'is_active': True, 'is_default': True}
        )

        if default_payment_method:
            await user_payment_method_crud.update(
                session,
                {'id': default_payment_method.id}, {'is_default': False}
            )

        await user_payment_method_crud.update(
            session, {'id': payment_method.id}, {'is_default': True}
        )

    async def add(
            self,
            session: AsyncSession,
            provider_name: str,
            provider_payment_method_id: str,
            payment_method_type: PaymentMethod,
            payload: dict
    ):
        """Вызывается в webhooks-эндпоинтах после получения сообщения от
        платёжных провайдеров о добавлении способа оплаты."""
        self.logger.debug(
            f'Запрос на добавление способа оплаты провайдера {provider_name} ('
            f'{provider_payment_method_id}): {payment_method_type} - '
            f'{payload} пользователю {self.user_id}'
        )

        provider = await provider_crud.get(session, {'name': provider_name})

        if provider is None:
            self.logger.error(f'Провайдера {provider} не существует')
            return

        user_payment_methods = await user_payment_method_crud.get_all(
            session, {'user_id': self.user_id, 'is_active': True}
        )

        await user_payment_method_crud.create(
            session,
            {
                'user_id': self.user_id,
                'type': payment_method_type,
                'payload': payload,
                'is_default': len(user_payment_methods) == 0,
                'provider_id': provider.id,
                'provider_payment_method_id': provider_payment_method_id
            }
        )

    async def remove(
            self,
            session: AsyncSession,
            provider_name: str,
            provider_payment_method_id: str
    ):
        """Вызывается в webhooks-эндпоинтах после получения сообщения от
        платёжных провайдеров об удалении способа оплаты."""
        self.logger.debug(
            f'Запрос на удаление способа оплаты провайдера {provider_name} ('
            f'{provider_payment_method_id}) у пользователя {self.user_id}'
        )
        provider = await provider_crud.get(session, {'name': provider_name})

        deleted_payment_method = await user_payment_method_crud.update(
            session,
            {
                'user_id': self.user_id,
                'provider_id': provider.id,
                'provider_payment_method_id': provider_payment_method_id
            },
            {'is_active': False}
        )

        if deleted_payment_method and deleted_payment_method[0].is_default:
            # Если удалённый способ оплаты использовался по-умолчанию,
            # назначаем первый способ из оставшихся способом по-умолчанию
            payment_methods = await user_payment_method_crud.get_all(
                session,
                {
                    'user_id': deleted_payment_method[0].user_id,
                    'is_active': True
                }
            )
            if payment_methods:
                await user_payment_method_crud.update(
                    session,
                    {'id': payment_methods[0].id},
                    {'is_default': True}
                )


async def get_payment_method_manager_di(
        authorize: AuthJWT = fastapi.Depends(),
) -> PaymentMethodManager:
    """Возвращает менеджер способов оплаты пользователя, направившего запрос.
    Применяется в эндпоинтах."""
    return PaymentMethodManager(
        uuid.UUID(await authorize.get_jwt_subject()), logger_factory(__name__)
    )


async def get_payment_method_manager(
        user_id: uuid.UUID | str
) -> PaymentMethodManager:
    """Возвращает менеджер способов оплаты переданного пользователя."""
    user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    return PaymentMethodManager(user_id, logger_factory(__name__))
