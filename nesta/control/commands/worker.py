import subprocess
from nesta.tasks import app
from nesta.control.commands.base import Base, Response


class Worker(Base):
    def __init__(self, configs):
        super(Worker, self).__init__("schedule", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.required = True
        subparsers.add_parser("start")
        subparsers.add_parser("restart")
        subparsers.add_parser("terminate")
        subparsers.add_parser("ping")

    def _execute(self, option):
        data = None
        msg = ""
        if option.command == "start":
            run_list = [
                "bash ~/src/nesta/bin/run_worker.sh &",
                f"ssh -f hspark@ec2-3-87-14-67.compute-1.amazonaws.com 'bash ~/git/nesta/bin/run_worker.sh'",
            ]
            for cmd in run_list:
                subprocess.call(
                    cmd,
                    shell=True
                )
        elif option.command == "terminate":
            app.control.broadcast("shutdown")
        elif option.command == "ping":
            data = app.control.ping()
        else:
            raise ValueError(f"Undefined command: {option.command}")

        return Response(
            exitcode=0,
            data=data,
            msg=msg
        )
