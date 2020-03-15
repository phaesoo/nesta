import pickle
from .base_control import BaseControl
from regista.utils.rabbitmq import RabbitMQClient


class ServerControl(BaseControl):
    def __init__(self):
        super(ServerControl, self).__init__("server")

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.add_parser("resume")
        subparsers.add_parser("stop")
        subparsers.add_parser("terminate")

    def _main(self, option):
        queue = RabbitMQClient()
        queue.init(
            host="localhost",
            port=5672,
            username="test",
            password="test",
            virtual_host="regista_server"
        )

        queue.queue_declare("server")

        queue.publish("server", {
            "data": {
                "command": option.command
            }
        })
