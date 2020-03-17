import os
import time
import subprocess
import yaml
from argparse import ArgumentParser
from celery import Celery


SCRIPT_PATH="/home/phaesoo/src/regista/temp/script"


def get_app(backend, broker, **kwargs):
    app = Celery("tasks", backend=backend, broker=broker)

    @app.task(name="script")
    def script(job_name):
        script_path = os.path.join(SCRIPT_PATH, job_name, "main.sh")
        if not os.path.exists(script_path):
            raise FileNotFoundError(script_path)
        return subprocess.call(script_path, shell=True)

    return app
