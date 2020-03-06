import time
import pickle
import logging
from .handler import *
from .define import define
from regista.utils.queue import SQSClient


QUEUE_URl="https://sqs.ap-northeast-2.amazonaws.com/924873670641/regista_server"

SERVER_QUEUE="server"
HANDLER_QUEUE="handler"


logger = logging.getLogger()


class Server:
    def __init__(self, mode):
        self._mode = mode
        self._server_queue = SQSClient(QUEUE_URl)

    def run(self):
        is_run = True

        while True:
            # server queue has high priority
            result = self._server_queue.receive_message()
            if result:
                data = result["data"]
                receipt_handle = result["receipt_handle"]

                cmd = data.get("command", None)
                by = data.get("by", "undefined")
                if cmd == "terminate":
                    logging.critical(f"Server is terminated by {by}")
                    break
                elif cmd == "stop":
                    is_run = False
                    logging.info(f"Server is stopped by {by}")
                elif cmd == "resume":
                    is_run = True
                    logging.info(f"Server is resumed by {by}")
                else:
                    logging.info(f"Server is resumed by {by}")
                    pass

                self._server_queue.delete_message(receipt_handle)
                
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