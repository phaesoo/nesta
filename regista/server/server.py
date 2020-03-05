import time
import pika
import pickle
import logging
from .handler import *
from .define import define

AMQP_HOST="ec2-3-87-14-67.compute-1.amazonaws.com"
AMQP_PORT=5672
AMQP_USER="prod"
AMQP_PSWD="12345"

SERVER_QUEUE="server"
HANDLER_QUEUE="handler"


logger = logging.getLogger()


class Server:
    def __init__(self, mode):
        self._mode = mode
        self._init_connection()

    def _init_connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=AMQP_HOST,
                port=AMQP_PORT,
                credentials=pika.PlainCredentials(username=AMQP_USER, password=AMQP_PSWD)
            )
        )
        self._connection = connection
        self._channel = connection.channel()

    def _get_queue(self, queue):
        retry_count = 0

        pickled = None
        while retry_count < 5:
            try:
                if self._connection.is_closed:
                    self._init_connection()
                    retry_count += 1
                
                _, _, pickled = self._channel.basic_get(queue, auto_ack=True)
            except:
                retry_count += 1
                time.sleep(0.5)
                continue
            else:
                break

        if pickled is None:
            raise ValueError("Connection error with AMQP")
        return pickle.loads(pickled)

    def run(self):
        attempts = 0
        is_run = True

        while True:
            if self._connection.is_closed:
                self._init_connection()
                attempts += 1
                continue
            
            # server queue has high priority
            data = self._get_queue(SERVER_QUEUE)
            if data:
                command = data.get("command", None)
                by = data.get("by", "undefined")
                if command == "terminate":
                    logging.critical(f"Server is terminated by {by}")
                    break
                elif command == "stop":
                    is_run = False
                    logging.info(f"Server is stopped by {by}")
                elif command == "resume":
                    is_run = True
                    logging.info(f"Server is resumed by {by}")
                else:
                    logging.info(f"Server is resumed by {by}")
                    pass
                
                continue
            
            if not is_run:
                time.sleep(1)
                continue

            # handler queue has sencond priority
            data = self._get_queue(HANDLER_QUEUE)
            if not data:
                time.sleep(1)
                continue

            title = data["title"]
            body = data["body"]

            if title == "result":
                handler = ResultHandler()
            else:
                print (f"Unknown title: {title}")
                continue
            
            time.sleep(1)

    def send_task(self):
        """
        Send task queue to celery broker
        """

        while True:
            pass