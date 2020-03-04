import sys
from argparse import ArgumentParser
from .controls import *


if __name__ == "__main__":
    parser = ArgumentParser
    argv = sys.argv[1:]
    if not len(argv):
        raise ValueError("Empty sys.argv[1:]")

    item = argv[0]

    control = None
    if item == "schedule":
        control = ScheduleControl()
    elif item == "server":
        control = ServerControl()
    elif item == "worker":
        control = WorkerControl()
    else:
        raise ValueError(f"Undefined item: {item}")

    control.main()