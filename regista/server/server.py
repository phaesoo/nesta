import time
import pika
import pickle
from .handler import *
from .define import define

AMQP_HOST="ec2-3-87-14-67.compute-1.amazonaws.com"
AMQP_PORT=5672
AMQP_USER="prod"
AMQP_PSWD="12345"

SERVER_QUEUE="server"



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

    def run(self):
        while True:
            if self._connection.is_closed:
                self._init_connection()
            
            attempts = 0
            while True:
                method_frame, pickled = None, None
                try:
                    method_frame, _, pickled = self._channel.basic_get(SERVER_QUEUE)
                except Exception as e:
                    print (e)
                    attempts += 1
                    time.sleep(1)
                    continue
                else:
                    attempts = 0
                
                data = pickle.loads(pickled)
                title = data["title"]
                body = data["body"]

                if title == "server":
                    handler = ServerHandler()
                elif title == "result":
                    handler = ResultHandler()
                else:
                    print (f"Unknown title: {title}")
                    continue

                result_code, msg = handler.handle(body)
                if result_code == define.TERMINATE_SERVER:
                    break
                elif result_code == define.STOP_SERVER:
                    pass
                elif result_code == define.STOP_SERVER:
                    pass
                else:
                    print (f"Undefined result_code: {result_code}")

                # acknowledge after action
                self._channel.basic_ack(method_frame.delivery_tag)
                time.sleep(1)

    def send_task(self):
        """
        Send task queue to celery broker
        """

        while True:
            pass