from argparse import ArgumentParser
from threading import Thread
from .server import Server


def parse_option():
    parser = ArgumentParser("Regista server")
    parser.add_argument("--mode", "-m", dest="mode", type=str, default="debug", help="{prod, debug}")
    parser.add_argument("--config_path", dest="config_path", type=str, help="conifg file path")
    return parser.parse_args()

if __name__ == "__main__":
    option = parse_option()

    server = Server(option.mode)
    server.run()

    t = Thread(target=server.send_task)
    t.start()
    t.join()
