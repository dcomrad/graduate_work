import logging
from sys import stdout

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOG_DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def get_configured_logger(logger_name: str) -> logging.Logger:
    """Генерирует логгер по заданному имени."""
    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler(stdout)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DT_FORMAT)
    c_handler.setFormatter(formatter)

    logger.addHandler(c_handler)

    return logger


logger = get_configured_logger(__name__)