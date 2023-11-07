import abc
import logging

import pydantic
from src.core.exceptions import NotFoundException
from src.models.models import Subscription
from src.schemas import HTMLForm
from src.services.external import AuthAPI, get_auth_api


class ProviderManager(abc.ABC):
    """Базовый класс для взаимодействия с провайдерами платежей."""

    PAYMENT_METHOD_NOT_FOUND = 'Способа оплаты {payment_method} не существует'
    PAYMENT_METHOD_FORBIDDEN_OR_DELETED = (
        'Способ оплаты {payment_method} не принадлежит клиенту {user} или был '
        'удален ранее'
    )
    TRANSACTION_NOT_FOUND = 'Транзакции {transaction} не существует'
    TRANSACTION_ALREADY_REFUNDED = (
        'Денежные средства по транзакции {transaction} были возвращены ранее'
    )

    def __init__(
            self,
            webhook_url: pydantic.HttpUrl,
            logger: logging.Logger,
            auth_api: AuthAPI = get_auth_api()
    ):
        """
        :param webhook_url: URL эндпоинта, используемый для оповещения о
        событиях со стороны провайдера платежей
        """
        self.webhook_url = webhook_url
        self.logger = logger
        self.auth_api = auth_api

    class NotFound(NotFoundException):
        pass

    @abc.abstractmethod
    async def add_payment_method(
            self,
            user_id: str,
            button_text: str,
            return_url: str
    ) -> HTMLForm:
        """Создаёт запрос на добавление нового способа оплаты.
        :param user_id: ID клиента
        :param button_text: Текст на кнопке отправки данных формы
        :param return_url: Ссылка, которая будет открыта после нажатия на
        кнопку отправки данных формы
        :return: HTML-код формы добавления нового способа оплаты
        """
        pass

    @abc.abstractmethod
    async def remove_payment_method(
            self,
            user_id: str,
            payment_method_id: str
    ):
        """Удаляет сохранённый способ оплаты клиента.
        :param user_id: ID клиента
        :param payment_method_id: ID способа оплаты на стороне провайдера
        """
        pass

    @abc.abstractmethod
    async def charge(
            self,
            user_id: str,
            payment_method_id: str,
            subscription: Subscription,
            idempotency_key: str
    ):
        """Взимает с пользователя плату за подписку.
        :param user_id: ID клиента
        :param payment_method_id: ID способа оплаты на стороне провайдера
        :param subscription: купленная подписка
        :param idempotency_key: ключ идемпотентности, используемый для
        исключения двойного списания средств
        """
        pass

    @abc.abstractmethod
    async def refund(
            self,
            transaction_id: str,
            reason: str
    ):
        """Возвращает пользователю денежные средства за ранее купленную
        подписку.
        :param transaction_id: ID совершённой на стороне провайдера операции
        :param reason: причина возврата средств
        """
        pass
