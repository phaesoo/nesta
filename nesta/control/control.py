import os
import sys
import socket
import yaml
from argparse import ArgumentParser, REMAINDER
from nesta.configs.util import parse_env, parse_config
from nesta.control.controls.server import Server
from nesta.control.controls.worker import Worker
from nesta.control.controls.schedule import Schedule


class Control:
    commands = {
        "server": Server,
        "worker": Worker,
        "schedule": Schedule,
    }
    
    def __init__(self, configs):
        self._configs = configs

    def execute(self, command, argv):
        assert isinstance(argv, list)

        cmd = self.commands.get(command)
        if cmd is None:
            print (f""""
            commands: {self.commands.keys()}
            Type 'control <command> --help' for help using a specific command.'
            """)
            return

        ctrl = cmd(self._configs)
        return ctrl.execute(argv)

if __name__ == "__main__":
    env_dict = parse_env()
    configs = parse_config(env_dict["CONFIG_PATH"])
    ctrl = Control(configs=configs)
    ctrl.execute(command=sys.argv[1], argv=sys.argv[2:])
