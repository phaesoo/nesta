import os
import sys
import socket
import yaml
from nesta.configs.util import parse_env, parse_config
from nesta.control.commands.base import Response
from nesta.control.commands.server import Server
from nesta.control.commands.worker import Worker
from nesta.control.commands.schedule import Schedule


class Control:
    commands = {
        "server": Server,
        "worker": Worker,
        "schedule": Schedule,
    }

    def __init__(self, configs):
        self._configs = configs
        self._help = "commands: {}\nType 'control <command> --help' for help using a specific command.'".format(
            list(self.commands.keys()))

    def execute(self, command, argv):
        try:
            return self._execute(command, argv)
        except Exception as e:
            return Response(
                exitcode=1,
                msg="exception: {}\n".format(e) + self._help
            )

    def _execute(self, command, argv):
        assert isinstance(argv, list)

        if command in ("help", "--help", "-h"):
            return Response(
                exitcode=0,
                msg=self._help
            )

        cmd = self.commands.get(command)
        if cmd is None:
            return Response(
                exitcode=0,
                msg="Unknown command: {}\n{}".format(command, self._help)
            )
        ctrl = cmd(self._configs)
        return ctrl.execute(argv)


if __name__ == "__main__":
    env_dict = parse_env()
    configs = parse_config(env_dict["MODE"])
    ctrl = Control(configs=configs)

    argv = sys.argv
    try:
        resp = ctrl.execute(command=sys.argv[1], argv=sys.argv[2:])
    except Exception as e:
        resp = ctrl.execute(command="help", argv=[])
    finally:
        if resp.exitcode != 0:
            print("exitcode: {}".format(resp.exitcode))
        if resp.data:
            print("data: {}".format(resp.data))
        print(resp.msg)
        sys.exit(resp.exitcode)
