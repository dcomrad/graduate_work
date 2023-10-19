from django.core.exceptions import ValidationError
from jinja2 import Environment, exceptions
from notification.logger import logger_factory

logger = logger_factory(__name__)


def validate_jinja_template(template: str) -> None:
    try:
        Environment().parse(template)
    except exceptions.TemplateSyntaxError as ex:
        logger.exception(ex)
        raise ValidationError('Синтаксическая ошибка в шаблоне')
