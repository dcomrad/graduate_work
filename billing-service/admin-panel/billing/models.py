import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .enums import (
    CurrencyChoices,
    RecurringIntervalChoices,
    TransactionStatusChoices,
)


class CustomJsonField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, dict):
            return value
        return super().from_db_value(value, expression, connection)


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class UserPaymentMethod(UUIDMixin):
    type = models.CharField(max_length=10, blank=True, null=True)
    payload = CustomJsonField()
    is_default = models.BooleanField()
    provider = models.ForeignKey('Provider', models.DO_NOTHING)
    user_id = models.UUIDField()
    provider_payment_method_id = models.CharField(max_length=64)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_payment_method'


class Provider(UUIDMixin):
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'provider'

    def __str__(self):
        return self.name


class Subscription(UUIDMixin):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    is_active = models.BooleanField()
    recurring_interval = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=RecurringIntervalChoices.choices,
    )
    recurring_interval_count = models.SmallIntegerField()
    permission_rank = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(9), MinValueValidator(0)],
    )
    currency = models.CharField(
        max_length=10, blank=True, null=True, choices=CurrencyChoices.choices
    )

    class Meta:
        managed = False
        db_table = 'subscription'

    def actual_price(self):
        return self.price / 100

    def __str__(self):
        return self.name


class UserSubscription(UUIDMixin):
    user_id = models.UUIDField()
    subscription = models.ForeignKey(Subscription, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateField(blank=True, null=True)
    renew_to = models.UUIDField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'user_subscription'


class Transaction(UUIDMixin):
    provider = models.ForeignKey(Provider, models.DO_NOTHING)
    user_id = models.UUIDField()
    payment_method = models.ForeignKey(UserPaymentMethod, models.DO_NOTHING)
    provider_transaction_id = models.CharField(max_length=64)
    amount = models.IntegerField()
    subscription = models.ForeignKey(Subscription, models.DO_NOTHING)
    currency = models.CharField(
        max_length=10, blank=True, null=True, choices=CurrencyChoices.choices
    )
    status = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=TransactionStatusChoices.choices,
    )
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction'

    def actual_amount(self):
        return self.amount / 100
