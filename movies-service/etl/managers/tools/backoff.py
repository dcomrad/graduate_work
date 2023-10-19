import logging
from functools import wraps
from time import sleep
from typing import Callable


def backoff(start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10,
            attempt=1000) -> Callable:
    """
    Функция для повторного выполнения функции через некоторое время, если
    возникла ошибка.

    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param attempt: допустимое кол-во попыток
    :return: результат выполнения функции
    """

    def func_wrapper(func: Callable) -> Callable:

        @wraps(func)
        def inner(*args, **kwargs) -> Callable:
            sleep_time = start_sleep_time
            a = 1

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f'{e}. Ожидаем {sleep_time} прежде чем выполнить операцию повторно.')

                    if sleep_time < border_sleep_time:
                        sleep_time = min(start_sleep_time * (factor ** a),
                                         border_sleep_time)
                    else:
                        sleep_time = border_sleep_time

                    sleep(sleep_time)
                    a += 1
                    continue
                finally:
                    if a >= attempt:
                        raise Exception(f'Кол-во попыток превысило {attempt}!')

        return inner

    return func_wrapper
