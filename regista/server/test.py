from celery import Celery


app = Celery("tasks", brocker="amqp://test:test@localhost:5672")

@app.task
def add(x, y):
    return x + y