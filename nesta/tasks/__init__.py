from celery import Celery


app = Celery("tasks", backend="rpc://", broker="amqp://prod:12345@ec2-3-87-14-67.compute-1.amazonaws.com//")
