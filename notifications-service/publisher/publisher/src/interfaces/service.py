import typing


class BrokerService(typing.Protocol):
    def send(self):
        ...
