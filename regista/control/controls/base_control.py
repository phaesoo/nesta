import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser


class BaseControl(ABC):
    def __init__(self, title):
        argv = sys.argv[1:]
        if not len(argv):
            raise ValueError("Empty sys.argv[1:]")

        self.__argv = argv[1:]
        self._parser = ArgumentParser(description=f"Regista controller[{title}]")

    @abstractmethod
    def _init_parser(self):
        pass

    @abstractmethod
    def _main(self, option):
        pass

    def main(self):
        self._init_parser()
        self._main(self._parser.parse_args(self.__argv))