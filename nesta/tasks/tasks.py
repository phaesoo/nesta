import os
import time
import subprocess
import yaml
from argparse import ArgumentParser
from celery import Celery


def get_app(**configs):
    broker = configs["services"]["common"]["celery"]["broker"] + "/nesta_worker"
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
