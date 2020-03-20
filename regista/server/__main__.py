import os
from argparse import ArgumentParser
from threading import Thread
from regista.utils.log import init_logger
from regista.configs.util import parse_config, get_defined_path
from .server import Server


def parse_arguments():
    parser = ArgumentParser("Regista server")
    parser.add_argument("--config_path", dest="config_path",
                        type=str, help="conifg file path")
    parser.add_argument("--daemonize", "-d", dest="daemonize",
                        type=bool, default=True, help="daemonize or not")
    return parser.parse_args()


if __name__ == "__main__":
    option = parse_arguments()
    assert os.path.exists(option.config_path)

    configs = parse_config(option.config_path)
    init_logger(get_defined_path(configs["services"]["server"]["log_path"], configs), "server")
    server = Server(configs=configs)
    if option.daemonize is True:
        server.start()
    else:
        server.run()
