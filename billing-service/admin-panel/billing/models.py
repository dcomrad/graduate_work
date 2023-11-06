import uuid

from django.db import models


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PaymentMethod(UUIDMixin):
    type = models.CharField(max_length=10, blank=True, null=True)
    payload = models.JSONField()
    is_default = models.BooleanField()
    provider = models.ForeignKey('Provider', models.DO_NOTHING)
    user_id = models.UUIDField()
    provider_payment_method_id = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'payment_method'


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
    price = models.SmallIntegerField()
    is_active = models.BooleanField()
    recurring_interval = models.CharField(max_length=10, blank=True, null=True)
    recurring_interval_count = models.SmallIntegerField()
    permission_rank = models.SmallIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscription'

    def __str__(self):
        return self.name


class UserSubscription(UUIDMixin):
    user_id = models.UUIDField()
    subscription = models.ForeignKey(Subscription, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateField(blank=True, null=True)
    auto_renewal = models.BooleanField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'user_subscription'


class Transaction(UUIDMixin):
    provider = models.ForeignKey(Provider, models.DO_NOTHING)
    user_id = models.UUIDField()
    payment_method = models.ForeignKey(PaymentMethod, models.DO_NOTHING)
    provider_transaction_id = models.CharField(max_length=64)
    amount = models.SmallIntegerField()
    subscription = models.ForeignKey(Subscription, models.DO_NOTHING)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction'
