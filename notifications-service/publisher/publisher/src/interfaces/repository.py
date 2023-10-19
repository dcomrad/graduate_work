import typing


class QueueRepository(typing.Protocol):
    def put_to_queue(self):
        ...
