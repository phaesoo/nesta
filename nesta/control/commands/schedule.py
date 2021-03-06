import datetime
from nesta.control.commands.base import Base, Response


class Schedule(Base):
    def __init__(self, configs):
        super(Schedule, self).__init__("schedule", configs)

    def _init_parser(self):
        subparsers = self._parser.add_subparsers(dest="command")
        subparsers.required = True
        insert_parser = subparsers.add_parser("insert")
        insert_parser.add_argument("--date", "-d", dest="date", type=str, required=True, help="'today', 'yyyymmdd'")

    def _execute(self, option):
        body = {
            "command": option.command
        }
        if option.command == "insert":
            if option.date == "today":
                body["date"] = datetime.date.today().strftime('%Y%m%d')
            else:
                body["date"] = option.date
        else:
            raise ValueError(f"Undefined command: {option.command}")
            
        self._publish(body)

        return Response(
            exitcode=0,
            data=None,
            msg=f"Schedule has been inserted, date: {option.date}",
        )
