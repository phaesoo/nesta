import pickle
from .base_control import BaseControl
from regista.utils.rabbitmq import RabbitMQClient


class ServerControl(BaseControl):
    def __init__(self, configs):
        super(ServerControl, self).__init__("server", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.add_parser("resume")
        subparsers.add_parser("stop")
        subparsers.add_parser("terminate")

    def _main(self, option):
        self._publish({
            "command": option.command
        })

        