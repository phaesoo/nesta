import time
import pika


class Server:
    def __init__(self, mode):
        self._mode = mode
        self._connection = self._init_connection()
        self._channel = self._connection.channel()

    def _init_connection(self):
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host="ec2-3-87-14-67.compute-1.amazonaws.com",
                port=5672,
                credentials=pika.PlainCredentials(username="prod", password="12345")
            )
        )

    def run(self):
        queue_state = self._channel.queue_declare("server")
        while True:
            self._channel.basic_get("server"))
            time.sleep(1)
            

    def send_task(self):
        """
        Send task queue to celery broker
        """

        while True:
            pass