import os
import time
import subprocess
import yaml
from argparse import ArgumentParser
from celery import Celery


def get_app(backend, broker, script_path="/home/phaesoo/src/nesta/temp/script", **kwargs):
    app = Celery("tasks", backend=backend, broker=broker)

    @app.task(name="script")
    def script(job_name):
        filepath = os.path.join(script_path, f"{job_name}.sh")
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)
        return subprocess.call(filepath, shell=True)

    return app
