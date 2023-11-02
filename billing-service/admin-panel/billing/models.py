import uuid

from django.db import models


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Provider(UUIDMixin):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'provider'

    def __str__(self):
        return self.name


class Subscription(UUIDMixin):
    name = models.CharField(max_length=120)
    price = models.SmallIntegerField()
    is_active = models.BooleanField()
    recurring_interval = models.CharField(max_length=10)
    recurring_interval_count = models.SmallIntegerField()
    permission_rang = models.SmallIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'subscription'

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user_id = models.UUIDField(primary_key=True)
    subscription = models.ForeignKey(Subscription, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateField(blank=True, null=True)
    auto_reneval = models.BooleanField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'user_subscription'


class Transaction(UUIDMixin):
    provider = models.ForeignKey(Provider, models.DO_NOTHING)
    idempotency_key = models.UUIDField()
    user = models.ForeignKey(
        UserSubscription,
        to_field='user_id',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    amount = models.SmallIntegerField()
    subscription = models.ForeignKey(
        Subscription, models.DO_NOTHING, blank=True, null=True
    )
    status = models.CharField(max_length=40)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction'
