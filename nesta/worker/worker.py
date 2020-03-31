import os
from celery.bin import worker
from celery import Celery
from argparse import ArgumentParser
from nesta.tasks.tasks import get_app
from nesta.configs.util import parse_env, parse_config


def parse_arguments():
    parser = ArgumentParser()
    return parser.parse_args()


if __name__ == "__main__":
    env_dict = parse_env()

    options = parse_arguments()

    configs = parse_config(env_dict["MODE"])

    script_path = configs["services"]["worker"]["script_path"]
    app = get_app(script_path=script_path, **configs["services"]["common"]["celery"])

    w = worker.worker(app=app)
    w.run(loglevel="INFO", traceback=True)

"""
import subprocess


if __name__ == "__main__":
    server_list = [
        "ec2-3-87-14-67.compute-1.amazonaws.com",
    ]

    for server in server_list:
        subprocess.call(
            f"ssh -f {server} 'bash ~/git/nesta/bin/run_worker.sh'",
            shell=True
        )
"""
