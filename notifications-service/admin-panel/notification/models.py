import uuid

from django.contrib.postgres import fields
from django.db import models
from jinja2 import Environment, meta
from notification.validators import validate_jinja_template


class DeliveryType(models.TextChoices):
    SMS = 'sms', 'SMS'
    EMAIL = 'email', 'Email'
    PUSH = 'push', 'Push'
    TELEGRAM = 'telegram', 'Telegram'


class Template(models.Model):
    id = models.UUIDField(  # noqa:VNE003
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    type = models.CharField(  # noqa:VNE003
        max_length=10,
        choices=DeliveryType.choices,
        verbose_name='Способ уведомления'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название уведомления'
    )
    title = models.CharField(
        max_length=255,
        validators=[validate_jinja_template],
        verbose_name='Заголовок'
    )
    content = models.TextField(
        validators=[validate_jinja_template],
        verbose_name='Содержимое'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    placeholders = fields.ArrayField(
        models.CharField(max_length=255),
        blank=True,
        verbose_name='Список переменных',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего обновления'
    )

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'
        db_table = 'notification"."template'

    def save(self, *args, **kwargs):
        env = Environment()
        title_vars = meta.find_undeclared_variables(env.parse(self.title))
        content_vars = meta.find_undeclared_variables(env.parse(self.content))
        self.placeholders = list(title_vars | content_vars)
        super().save(*args, **kwargs)


class ExternalUser(models.Model):
    login = models.TextField(verbose_name='Логин')
    full_name = models.TextField(verbose_name='ФИО')
    email = models.TextField(verbose_name='Электронная почта')
    time_zone = models.TextField(verbose_name='Часовой пояс')
    notifications_enabled = models.BooleanField(verbose_name='Уведомления включены')  # noqa:E501

    class Meta:
        verbose_name = 'Пользователь сервиса'
        verbose_name_plural = 'Пользователи сервиса'
