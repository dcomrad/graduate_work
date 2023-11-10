from django.db.models import TextChoices


class RecurringIntervalChoices(TextChoices):
    MONTH = 'month'
    YEAR = 'year'


class CurrencyChoices(TextChoices):
    RUB = 'RUB'
    USD = 'USD'


class TransactionStatusChoices(TextChoices):
    DRAFT = 'draft'
    PROCESSING = 'processing'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    REFUNDED = 'refunded'
