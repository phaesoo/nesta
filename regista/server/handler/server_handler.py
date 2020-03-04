from .base_handler import BaseHandler
from regista.server.define import define

class ServerHandler(BaseHandler):
    """
    Server handler
    """
    def __init__(self):
        pass

    def _handle(self, body):
        command = body["command"]
        user = body["user"]

        if command == "terminate":
            return define.TERMINATE_SERVER, f"Terminated by {user}"
        elif command == "stop":
            return define.STOP_SERVER, f"Stopped by {user}"
        elif command == "resume":
            return define.RESUME_SERVER, f"Resummed by {user}"
        else:
            return define.UNKNOWN_COMMAND, ""

