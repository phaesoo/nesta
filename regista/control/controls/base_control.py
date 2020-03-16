import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser


class BaseControl(ABC):
    def __init__(self, title, configs):
        self._argv = sys.argv[4:]
        self._parser = ArgumentParser(description=f"Regista controller[{title}]")
        self._configs = configs        

    @abstractmethod
    def _init_parser(self):
        pass

    @abstractmethod
    def _main(self, option):
        pass

    def main(self):
        self._init_parser()
        self._main(self._parser.parse_args(self._argv))