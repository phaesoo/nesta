from nesta.control.commands.base import Base, Response


class Server(Base):
    def __init__(self, configs):
        super(Server, self).__init__("server", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.required = True
        subparsers.add_parser("resume")
        subparsers.add_parser("stop")
        subparsers.add_parser("terminate")
        subparsers.add_parser("status")
        subparsers.add_parser("ping")
        subparsers.add_parser("summary")


    def _execute(self, option):
        data = None
        msg = ""
        if option.command == "ping":
            msg="Recieved message from server: {}".format(self._send("hi"))
        elif option.command == "status":
            data = self._send("status")
            msg="Current server status: {}".format(data)
        elif option.command == "summary":
            data = self._send("summary")
            msg="[Summary]\n{}".format(data)
        elif option.command in ["stop", "resume", "terminate"]:
            self._publish({
                "command": option.command
            })
            msg="Send command to server: {}".format(option.command)
        else:
            raise ValueError("Undefined command: {}".format(option.command))

        return Response(
            exitcode=0,
            data=data,
            msg=msg,
        )
