import subprocess
from regista.tasks import app
from .base_control import BaseControl


class WorkerControl(BaseControl):
    def __init__(self):
        super(WorkerControl, self).__init__("schedule")

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.add_parser("start")
        subparsers.add_parser("restart")
        subparsers.add_parser("terminate")
        subparsers.add_parser("ping")

    def _main(self, option):
        if option.command == "start":
            run_list = [
                "bash ~/src/regista/bin/run_worker.sh &",
                f"ssh -f hspark@ec2-3-87-14-67.compute-1.amazonaws.com 'bash ~/git/regista/bin/run_worker.sh'",
            ]
            for cmd in run_list:
                subprocess.call(
                    cmd,
                    shell=True
                )
        elif option.command == "terminate":
            app.control.broadcast("shutdown")
        elif option.command == "ping":
            print (app.control.ping())
        else:
            raise ValueError(f"Undefined command: {option.command}")
