import functools
import logging
import pathlib
import uuid

import jinja2
import pydantic
import stripe
from src.config.config import settings
from src.core.logger import logger_factory
from src.providers.base import HTMLForm, ProviderManager
from stripe.api_resources import Customer
from stripe.error import InvalidRequestError
from stripe.error import SignatureVerificationError  # noqa


class StripeProviderManager(ProviderManager):
    """Класс для взаимодействия с провайдером платежей Stripe."""

    TEMPLATE_NOT_FOUND = 'Не найден файл шаблона'

    ENABLED_EVENTS = [
        'payment_method.attached',
        'payment_method.detached',
        'payment_intent.processing',
        'payment_intent.succeeded',
        'payment_intent.payment_failed',
        'charge.refunded'
    ]

    def __init__(
            self,
            secret_key: str,
            publishable_key: str,
            add_card_template: pathlib.Path,
            webhook_url: pydantic.HttpUrl,
            logger: logging.Logger = logger_factory(__name__)
    ):
        """
        :param secret_key: Секретный ключ API Stripe
        :param publishable_key: Публичный ключ API Stripe
        :param add_card_template: Путь к файлу с jinja-шаблоном формы
        добавления нового способа оплаты
        :param webhook_url: URL эндпоинта, используемый для оповещения о
        событиях со стороны Stripe
        """
        super().__init__(webhook_url, logger)
        if not add_card_template.exists():
            self.logger.error(f'{self.TEMPLATE_NOT_FOUND}:{add_card_template}')
            raise self.NotFound(self.TEMPLATE_NOT_FOUND)

        self.stripe = stripe
        self.stripe.api_key = secret_key
        self.stripe.publishable_key = publishable_key
        self.add_card_template = add_card_template

        self._check_or_create_webhook(self.webhook_url)

    def _check_or_create_webhook(
            self,
            url: str
    ) -> None:
        for webhook in self.stripe.WebhookEndpoint.list():
            if webhook.url == url:
                return

        self.stripe.WebhookEndpoint.create(
            url=url,
            enabled_events=self.ENABLED_EVENTS
        )

    async def _get_or_create_customer(
            self,
            user_id: str
    ) -> Customer:
        try:
            customer = self.stripe.Customer.retrieve(user_id)
        except InvalidRequestError:
            user = await self.auth_api.get_user(uuid.UUID(user_id))
            customer = self.stripe.Customer.create(
                id=str(user.id),
                name=user.full_name,
                email=user.email
            )

        return customer

    async def _check_payment_method(
            self,
            user_id: str,
            payment_method_id: str
    ) -> None:
        try:
            payment_method = self.stripe.PaymentMethod.retrieve(
                payment_method_id
            )
        except InvalidRequestError:
            msg = self.PAYMENT_METHOD_NOT_FOUND.format(
                payment_method=payment_method_id
            )
            self.logger.error(msg)
            raise self.NotFound(msg)

        customer = await self._get_or_create_customer(user_id)
        if payment_method.customer != customer.id:
            msg = self.PAYMENT_METHOD_FORBIDDEN_OR_DELETED.format(
                payment_method=payment_method_id, user=user_id
            )
            self.logger.error(msg)
            raise self.NotFound(msg)

    async def _check_transaction(
            self,
            payment_intent_id: str,
    ) -> None:
        try:
            self.stripe.PaymentIntent.retrieve(payment_intent_id)
        except InvalidRequestError:
            msg = self.TRANSACTION_NOT_FOUND.format(
                transaction=payment_intent_id
            )
            self.logger.error(msg)
            raise self.NotFound(msg)

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
        self.logger.debug(
            f'Запрос на добавление нового способа оплаты пользователю '
            f'{user_id} ("{button_text}", "{return_url}")'
        )
        customer = await self._get_or_create_customer(user_id)

        setup_intent = self.stripe.SetupIntent.create(
            customer=customer.id,
            payment_method_types=['card'],
        )

        with open(self.add_card_template) as file:
            template = jinja2.Template(file.read())

            return template.render(
                BUTTON_TEXT=button_text,
                PUBLISHABLE_KEY=self.stripe.publishable_key,
                CLIENT_SECRET=setup_intent.client_secret,
                RETURN_URL=return_url
            )

    async def remove_payment_method(
            self,
            user_id: str,
            payment_method_id: str
    ):
        """Удаляет способ оплаты клиента.
        :param user_id: ID клиента
        :param payment_method_id: ID способа оплаты на стороне провайдера
        """
        self.logger.debug(
            f'Запрос на удаление способа оплаты {payment_method_id} '
            f'у пользователя {user_id}'
        )
        await self._check_payment_method(user_id, payment_method_id)
        self.stripe.PaymentMethod.detach(payment_method_id)

    async def charge(
            self,
            user_id: str,
            payment_method_id: str,
            amount: int,
            currency: str,
            details: dict,
            idempotency_key: str
    ):
        """Взимает с пользователя плату за подписку.
        :param user_id: ID клиента
        :param payment_method_id: ID способа оплаты на стороне провайдера
        :param amount: оплачиваемая сумма в центах/копейках
        :param currency: валюта оплаты
        :param details: дополнительная информация, которая будет сохранена на
        стороне провайдера
        :param idempotency_key: ключ идемпотентности, используемый для
        исключения двойного списания средств
        """
        self.logger.debug(
            f'Запрос на взимание платы в размере {amount / 100} c '
            f'пользователя {user_id} со способом оплаты {payment_method_id}'
        )

        await self._check_payment_method(user_id, payment_method_id)
        self.stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=user_id,
            payment_method=payment_method_id,
            metadata={'transaction_id': idempotency_key, **details},
            idempotency_key=idempotency_key,
            confirm=True,
            off_session=True
        )

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
        self.logger.debug(
            f'Запрос на возмещение средств по транзакции {transaction_id} '
            f'по причине {reason}'
        )
        await self._check_transaction(transaction_id)
        try:
            self.stripe.Refund.create(
                payment_intent=transaction_id,
                metadata={'reason': reason}
            )
        except InvalidRequestError:
            msg = self.TRANSACTION_ALREADY_REFUNDED.format(
                transaction=transaction_id
            )
            self.logger.error(msg)
            raise self.NotFound(msg)


@functools.cache
def get_stripe_manager() -> StripeProviderManager:
    return StripeProviderManager(
        settings.stripe.secret_key,
        settings.stripe.publishable_key,
        settings.stripe.template_dir / 'add_card.html',
        settings.stripe.webhook_url
    )
