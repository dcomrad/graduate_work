import logging
from functools import wraps
from sys import stdout
from time import sleep

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


def backoff(exception, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если
    возникла ошибка. Использует наивный экспоненциальный рост времени повтора
    (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        time = start_sleep_time * 2^(n) if time < border_sleep_time
        time = border_sleep_time if time >= border_sleep_time
    :param exception: тип ошибки, который перехвачивает функция
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                inner.fail_count = 0
                return result
            except exception as ex:
                time = start_sleep_time * pow(factor, inner.fail_count)
                if time > border_sleep_time:
                    time = border_sleep_time
                else:
                    inner.fail_count += 1
                msg = 'Сбой вызова {function}: {msg}. Повтор через {time} с.'
                logger.error(
                    msg.format(function=func.__name__,
                               msg=str(ex).replace('\n', ' '), time=time)
                )
                sleep(time)
                return inner(*args, **kwargs)

        inner.fail_count = 0
        return inner
    return wrapper
