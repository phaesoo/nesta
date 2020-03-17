import os
import sys
import socket
import yaml
from argparse import ArgumentParser, REMAINDER
from .controls import *


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--item", dest="item",
                        help="{schedule, server, worker}", required=True)
    parser.add_argument("--config_path", dest="config_path",
                        help="config path", required=True)
    return parser.parse_args(sys.argv[1:3])


if __name__ == "__main__":
    option = parse_arguments()
    assert os.path.exists(option.config_path)

    control = None
    if option.item == "schedule":
        control = ScheduleControl
    elif option.item == "server":
        control = ServerControl
    elif option.item == "worker":
        control = WorkerControl
    else:
        raise ValueError(f"Undefined item: {option.item}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 9999))
    client_socket.sendall("hi".encode())

    data = client_socket.recv(1024)
    print (data.decode())

    ctrl = control(configs=yaml.load(
        open(option.config_path), Loader=yaml.Loader))
    ctrl.main()
