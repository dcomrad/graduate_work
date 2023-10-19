import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt="%m.%d.%y %H:%M:%S", level=20)
base_logger = logging.getLogger()


def __base_log(msg, level='DEBUG'):
    """Запись лога
    :param text: сообщение
    :param level: уровень логирования (DEBUG, INFO, WARNING, ERROR)
    """
    try:
        msg = str(msg)
    except Exception as error:
        print("Не смогли преобразовать переданный в log объект к строке\n{0}".format(error))
        return
    level = logging.getLevelName(level)
    base_logger.log(level=level, msg=msg)


def log(msg):
    """Лог
    :param msg: сообщение
    """
    __base_log(msg=f'[l] {msg}', level='INFO')


def error(msg):
    """Ошибка
    :param msg: сообщение
    """
    __base_log(msg=f'[e] {msg}', level='ERROR')
