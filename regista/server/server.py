import time
import pickle
import logging
from .handler import *
from .define import define
from regista.utils.queue import SQSClient


MAIN_QUEUE_URl="https://sqs.ap-northeast-2.amazonaws.com/924873670641/regista_server"
SUB_QUEUE_URl="https://sqs.ap-northeast-2.amazonaws.com/924873670641/regista_server_sub"

SERVER_QUEUE="server"
HANDLER_QUEUE="handler"


logger = logging.getLogger()


class Server:
    def __init__(self, mode):
        self._mode = mode
        self._main_queue = SQSClient(MAIN_QUEUE_URl)
        self._sub_queue = SQSClient(SUB_QUEUE_URl)

    def run(self):
        is_run = True

        while True:
            # main queue has high priority
            result = self._main_queue.receive_message()
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

                self._main_queue.delete_message(receipt_handle)
                continue
            
            if not is_run:
                time.sleep(1)
                continue

            # sub queue has lower priority
            result = self._sub_queue.receive_message()
            if result is None:
                time.sleep(1)
                continue

            title = result["title"]
            body = result["body"]

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