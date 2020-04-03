import os
import sys
import time
import logging
from logging import handlers
import subprocess
import yaml
from argparse import ArgumentParser
from celery import Celery
from celery.signals import after_setup_logger
from nesta.utils.log import init_logger


def get_worker(**configs):
    broker = configs["services"]["common"]["celery"]["broker"]
    backend = configs["services"]["common"]["celery"]["backend"]

    app = Celery("tasks", broker=broker, backend=backend)
    app.conf.update(
        CELERY_TRACK_STARTED=True,
    )
    
    script_path = configs["services"]["worker"]["script_path"]

    @app.task(name="script")
    def script(job_name):
        filepath = os.path.join(script_path, f"{job_name}.sh")
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)
        return subprocess.call(filepath, shell=True)

    return app
