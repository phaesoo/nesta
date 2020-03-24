from abc import ABC, abstractmethod
from argparse import ArgumentParser


class Response:
    def __init__(self, exitcode, data=None, msg=""):
        assert isinstance(exitcode, int)
        assert isinstance(msg, str)
        self.exitcode = exitcode
        self.data = data
        self.msg = msg

    def __str__(self):
        return f"""
        exitcode: {self.exitcode}
        data: {self.data}
        msg: {self.msg}
        """


class Base(ABC):
    def __init__(self, title, configs):
        self._parser = ArgumentParser(
            description=f"Nesta admin tool[{title}]")
        self._title = title
        self._configs = configs

    def execute(self, argv):
        assert isinstance(argv, list)

        # parse arguments
        self._init_parser()
        parsed = self._parser.parse_args(argv)

        try:
            resp = self._execute(parsed)
            assert isinstance(resp, Response)
            return resp
        except Exception as e:
            return Response(
                exitcode=1,
                data=None,
                msg=f"Unexpected error: {e}"
            )

    @abstractmethod
    def _init_parser(self):
        pass

    @abstractmethod
    def _execute(self, option):
        pass
