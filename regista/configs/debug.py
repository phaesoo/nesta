CELERY_BACKEND="rpc://"
CELERY_BORKER="amqp://test:test@localhost/regista_worker"

SERVER_QUEUE="server"


MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "test",
    "password": "test",
    "db": "regista",
}