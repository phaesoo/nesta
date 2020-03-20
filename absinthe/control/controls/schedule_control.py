from .base_control import BaseControl


class ScheduleControl(BaseControl):
    def __init__(self, configs):
        super(ScheduleControl, self).__init__("schedule", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        insert_parser = subparsers.add_parser("insert")
        insert_parser.add_argument("--date", "-d", dest="date", type=str)

    def _main(self, option):
        body = {
            "command": option.command
        }
        if option.command == "insert":
            body["date"] = option.date
        else:
            raise ValueError(f"Undefined command: {option.command}")
            
        self._publish(body)
        