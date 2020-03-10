CELERY_BACKEND="rpc://"
CELERY_BORKER="amqp://prod:12345@ec2-3-87-14-67.compute-1.amazonaws.com//"

SERVER_QUEUE="server"


MYSQL_CONFIG = {
    "host": "ec2-3-87-14-67.compute-1.amazonaws.com",
    "port": 3306,
    "user": "hfcp",
    "password": "haaforhaafor",
    "db": "regista",
}