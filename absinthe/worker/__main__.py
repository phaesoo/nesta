import yaml
from celery.bin import worker
from celery import Celery
from argparse import ArgumentParser
from absinthe.tasks.tasks import get_app


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--config_path", dest="config_path", type=str, help="config pth", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    options = parse_arguments()

    configs = yaml.load(open(options.config_path), Loader=yaml.Loader)

    app = get_app(**configs["services"]["common"]["celery"])

    w = worker.worker(app=app)
    w.run(loglevel="INFO", traceback=True)
