import sys
import socket
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from absinthe.utils.rabbitmq import RabbitMQClient


class BaseControl(ABC):
    def __init__(self, title, configs):
        self._argv = sys.argv[4:]
        self._parser = ArgumentParser(
            description=f"Absinthe controller[{title}]")
        self._title = title
        self._configs = configs

        try:
            recv = self._send("hi")
            if recv == "hello":
                pass
            else:
                raise ValueError(recv)
        except ConnectionRefusedError:
            print ("Connection refused, server may not running.")
            sys.exit(1)
        except Exception as e:
            print (f"Unexpected error: {e}")
            sys.exit(1)

    def _send(self, msg):
        assert isinstance(msg, str)
        # server health check
        server_config = self._configs["services"]["server"]
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_config["host"], server_config["port"]))
        client_socket.sendall(msg.encode())
        return client_socket.recv(1024).decode()

    @abstractmethod
    def _init_parser(self):
        pass

    @abstractmethod
    def _main(self, option):
        pass

    def _publish(self, body):
        assert isinstance(body, dict)
        mq_configs = self._configs["services"]["common"]["rabbitmq"]

        mq_client = RabbitMQClient()
        mq_client.init(**mq_configs)
        mq_client.publish(queue=mq_configs["queue"], data={
            "title": self._title,
            "body": body
        })

    def main(self):
        self._init_parser()
        self._main(self._parser.parse_args(self._argv))
