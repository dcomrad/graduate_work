import logging
from sys import stdout

from config.base_settings import logger_settings

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOG_DT_FORMAT = '%d.%m.%Y %H:%M:%S'

logger = logging.getLogger(__name__)

logger.setLevel(logger_settings.loglevel)

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DT_FORMAT)
c_handler = logging.StreamHandler(stdout)
c_handler.setFormatter(formatter)

logger.addHandler(c_handler)
