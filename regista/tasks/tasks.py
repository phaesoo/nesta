import os
import time
import subprocess
from celery import Celery
from regista.configs import debug


app = Celery("tasks", backend=debug.CELERY_BACKEND, broker=debug.CELERY_BORKER)


SCRIPT_PATH="/home/hspark/git/regista/temp/script"

@app.task
def add(x, y):
    return x + y
    
@app.task
def script(job_name):
    script_path = os.path.join(SCRIPT_PATH, job_name, "main.sh")
    if not os.path.exists(script_path):
        raise FileNotFoundError(script_path)
    return subprocess.call(script_path, shell=True)