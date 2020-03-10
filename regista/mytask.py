from celery import Celery
import time

app = Celery("mytask", backend="rpc://", broker="amqp://prod:12345@ec2-3-87-14-67.compute-1.amazonaws.com//")


@app.task
def add(x, y):
    return x + y


@app.task
def sleep_and_add(x, y):
    time.sleep(1000)
    return x + y


@app.task
def error():
    print ("value error")
    raise ValueError("error")
