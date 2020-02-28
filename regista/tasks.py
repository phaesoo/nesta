from celery import Celery
import time

app = Celery("tasks", backend="rpc://", broker="pyamqp://guest:guest@localhost//")


@app.task
def add(x, y):
    time.sleep(100)
    return x + y