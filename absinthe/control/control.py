import os
import sys
import socket
import yaml
from argparse import ArgumentParser, REMAINDER
from absinthe.configs.util import parse_env, parse_config
from absinthe.control.controls.server import Server
from absinthe.control.controls.worker import Worker
from absinthe.control.controls.schedule import Schedule


class Control:
    commands = {
        "server": Server,
        "worker": Worker,
        "schedule": Schedule,
    }
    
    def __init__(self, configs):
        self._configs = configs

    def main(self, command, argv):
        assert isinstance(argv, list)

        cmd = self.commands.get(command)
        if cmd is None:
            print (f""""
            commands: {self.commands.keys()}
            Type 'control <command> --help' for help using a specific command.'
            """)
        else:
            ctrl = cmd(self._configs)
            ctrl.main(argv)

if __name__ == "__main__":
    env_dict = parse_env()
    config_path = env_dict["CONFIG_PATH"]
    assert os.path.exists(config_path)

    configs = parse_config(config_path)
    ctrl = Control(configs=configs)
    ctrl.main(command=sys.argv[1], argv=sys.argv[2:])
