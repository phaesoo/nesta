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
        configs = self._configs["services"]["common"]["rabbitmq"]

        mq_client = RabbitMQClient()
        mq_client.init(**configs)

        mq_client.queue_declare(configs["queues"][0])
        mq_client.publish("server", {
            "data": {
                "command": option.command
            }
        })
