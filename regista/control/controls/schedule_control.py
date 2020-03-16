from .base_control import BaseControl


class ScheduleControl(BaseControl):
    def __init__(self, configs):
        super(ScheduleControl, self).__init__("schedule", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.add_parser("insert")

    def _main(self, option):
        print (option.command)
        if option.command == "insert":
            pass
        else:
            raise ValueError(f"Undefined command: {option.command}")
        