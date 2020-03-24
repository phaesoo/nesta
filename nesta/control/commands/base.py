import sys
import socket
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from nesta.utils.rabbitmq import RabbitMQClient


class Response:
    def __init__(self, exitcode, data=None, msg=""):
        assert isinstance(exitcode, int)
        assert isinstance(msg, str)
        self.exitcode = exitcode
        self.data = data
        self.msg = msg

    def __str__(self):
        return f"""
        exitcode: {self.exitcode}
        data: {self.data}
        msg: {self.msg}
        """

class Base(ABC):
    def __init__(self, title, configs):
        self._parser = ArgumentParser(
            description=f"Nesta controller[{title}]")
        self._title = title
        self._configs = configs

    def execute(self, argv):
        assert isinstance(argv, list)

        # parse arguments
        self._init_parser()
        parsed = self._parser.parse_args(argv)

        # server health check first
        try:
            recv = self._send("hi")
            if recv == "hello":
                pass
            else:
                raise ValueError(recv)
        except ConnectionRefusedError:
            return Response(
                exitcode=1,
                data=None,
                msg="Connection refused, server may not running."
            )
        except Exception as e:
            return Response(
                exitcode=1,
                data=None,
                msg=f"Unexpected error: {e}"
            )

        try:
            resp = self._execute(parsed)
            assert isinstance(resp, Response)
            return resp
        except Exception as e:
            return Response(
                exitcode=1,
                data=None,
                msg=f"Unexpected error: {e}"
            )

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
    def _execute(self, option):
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
