from .base_control import BaseControl


class ScheduleControl(BaseControl):
    def __init__(self):
        super(ScheduleControl, self).__init__("schedule")

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.add_parser("insert")

    def _main(self, option):
        if option.command:
            print ("here")