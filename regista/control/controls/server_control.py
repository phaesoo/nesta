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
        subparsers.add_parser("status")
        subparsers.add_parser("ping")

    def _main(self, option):
        if option.command == "ping":
            print (self._send("hi"))
        elif option.command == "status":
            print ("server status: {}".format(self._send("status")))
        elif option.command in ["stop", "resume", "terminate"]:
            self._publish({
                "command": option.command
            })
            print (f"Send command to server: {option.command}")
        else:
            raise ValueError(f"Undefined command: {option.command}")
