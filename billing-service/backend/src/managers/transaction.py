import uuid

import fastapi
from src.core.logger import logger_factory
from src.db.crud import transaction_crud
from src.db.postgres import AsyncSession
from src.jwt import AuthJWT
from src.managers.base import BaseManager
from src.models.models import Transaction, TransactionStatus


class TransactionManager(BaseManager):
    async def get_transactions(
            self,
            session: AsyncSession,
    ) -> list[Transaction]:
        self.logger.debug(
            f'Запрос всех транзакций пользователя {self.user_id}'
        )

        return await transaction_crud.get_all(
            session,
            {'user_id': self.user_id},
            sort='created_at desc'
        )

    async def get_or_create(
            self,
            session,
            created_data: dict
    ) -> Transaction:
        self.logger.debug(
            f'Запрос получения существующей или создания новой транзакции '
            f'({created_data})'
        )

        # ID записи в таблице Transaction используется, в качестве ключа
        # идемпотентности для выполнения запросов в провайдер платежей,
        # поэтому сначала ищем свежую транзакцию в статусе DRAFT, чтобы
        # исключить двойного запроса на списание средств
        transaction = await transaction_crud.get_all(
            session,
            {
                'user_id': self.user_id,
                'subscription_id': created_data['subscription_id'],
                'payment_method_id': created_data['payment_method_id'],
                'status': TransactionStatus.DRAFT,
            },
            sort='created_at desc',
            limit=1
        )

        if transaction:
            return transaction[0]

        # Создаём черновик новой транзакции
        return await transaction_crud.create(
            session,
            {'user_id': self.user_id, **created_data}
        )

    async def update(
            self,
            session,
            transaction_id: uuid.UUID,
            updated_data: dict
    ) -> list[Transaction]:
        self.logger.debug(
            f'Запрос обновления транзакции {transaction_id} ({updated_data})'
        )

        return await transaction_crud.update(
            session,
            {'user_id': self.user_id, 'id': transaction_id},
            {**updated_data}
        )


async def get_transaction_manager_di(
        authorize: AuthJWT = fastapi.Depends(),
) -> TransactionManager:
    """Возвращает менеджер транзакций пользователя, направившего запрос.
    Применяется в эндпоинтах."""
    return TransactionManager(
        uuid.UUID(await authorize.get_jwt_subject()), logger_factory(__name__)
    )


async def get_transaction_manager(
        user_id: uuid.UUID | str
) -> TransactionManager:
    """Возвращает менеджер транзакций переданного пользователя."""
    user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    return TransactionManager(user_id, logger_factory(__name__))
