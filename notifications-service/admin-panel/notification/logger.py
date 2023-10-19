import logging
from functools import cache
from logging.handlers import RotatingFileHandler
from sys import stdout

from notification.settings import settings


@cache
def logger_factory(name: str) -> logging.Logger:
    """Генерирует преднастроенный логгер по заданному имени."""
    logger = logging.getLogger(name)

    logger.setLevel(
        logging.DEBUG if settings.logging.debug else logging.CRITICAL
    )

    c_handler = logging.StreamHandler(stdout)
    f_handler = RotatingFileHandler(filename=settings.logging.log_file,
                                    maxBytes=10**6,
                                    backupCount=5,
                                    encoding='UTF-8')

    formatter = logging.Formatter(fmt=settings.logging.log_format,
                                  datefmt=settings.logging.dt_format)
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
