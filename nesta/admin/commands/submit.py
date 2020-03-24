from nesta.admin.commands.base import Base, Response


class Submit(Base):
    def __init__(self):
        pass

    def _init_parser(self):
        self._parser.add_argument("--skip_validation", "-s", dest="skip_validation", action="store_true", default=False)
        