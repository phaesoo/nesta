from argparse import ArgumentParser
from .server import Server


def parse_option():
    parser = ArgumentParser("Regista server")
    parser.add_argument("--mode", "-m", dest="mode", type=str, default="debug", help="{prod, debug}")
    return parser.parse_args()

if __name__ == "__main__":
    option = parse_option()

    server = Server(option.mode)
    server.run()
