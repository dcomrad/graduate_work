from django.db.models import TextChoices


class RecurringIntervalChoices(TextChoices):
    MONTH = 'month'
    YEAR = 'year'


class CurrencyChoices(TextChoices):
    RUB = 'RUB'


class TransactionStatusChoices(TextChoices):
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    PROCESSING = 'processing'
