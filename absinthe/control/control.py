import os
import sys
import socket
import yaml
from argparse import ArgumentParser, REMAINDER
from absinthe.control.controls import *
from absinthe.configs.util import parse_env, parse_config


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--item", dest="item",
                        help="{schedule, server, worker}", required=True)
    return parser.parse_args(sys.argv[1:3])


if __name__ == "__main__":
    env_dict = parse_env()
    config_path = env_dict["CONFIG_PATH"]
    assert os.path.exists(config_path)

    option = parse_arguments()
    control = None
    if option.item == "schedule":
        control = ScheduleControl
    elif option.item == "server":
        control = ServerControl
    elif option.item == "worker":
        control = WorkerControl
    else:
        raise ValueError(f"Undefined item: {option.item}")

    configs = parse_config(config_path)
    ctrl = control(configs=configs)
    ctrl.main()
