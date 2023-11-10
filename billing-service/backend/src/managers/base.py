import abc
import logging
import uuid


class BaseManager(abc.ABC):
    def __init__(
            self,
            user_id: uuid.UUID,
            logger: logging.Logger
    ):
        self.user_id = user_id
        self.logger = logger
