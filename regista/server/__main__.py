import os
from argparse import ArgumentParser
from threading import Thread
import yaml
from .server import Server


def parse_arguments():
    parser = ArgumentParser("Regista server")
    parser.add_argument("--mode", "-m", dest="mode", type=str, default="debug", help="{prod, debug}")
    parser.add_argument("--config_path", dest="config_path", type=str, help="conifg file path")
    return parser.parse_args()

if __name__ == "__main__":
    option = parse_arguments()
    assert os.path.exists(option.config_path)

    server = Server(
        configs=yaml.load(open(option.config_path), Loader=yaml.Loader)
        )
    server.run()

    t = Thread(target=server.update_result)
    t.start()
    t.join()
