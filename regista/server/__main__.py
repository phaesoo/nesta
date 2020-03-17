import os
import yaml
from argparse import ArgumentParser
from threading import Thread
from regista.utils.log import init_logger
from .server import Server


def parse_arguments():
    parser = ArgumentParser("Regista server")
    parser.add_argument("--mode", "-m", dest="mode", type=str, default="debug", help="{prod, debug}")
    parser.add_argument("--config_path", dest="config_path", type=str, help="conifg file path")
    return parser.parse_args()


if __name__ == "__main__":
    init_logger("server")

    option = parse_arguments()
    assert os.path.exists(option.config_path)

    server = Server(
        configs=yaml.load(open(option.config_path), Loader=yaml.Loader)
        )

    threads = [Thread(target=t) for t in [server.health_check, server.update_result]]

    for t in threads:
        t.start()

    server.run()
    
    for t in threads:
        t.join()
