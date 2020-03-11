import time
import pickle
import logging
from .define import define
from .schedule import Schedule
from regista.tasks.tasks import app, script
from regista.utils.queue import SQSClient
from regista.configs import debug
from regista.utils.mysql import MySQLClient
from regista.utils.log import init_logger


MAIN_QUEUE_URl="https://sqs.ap-northeast-2.amazonaws.com/924873670641/regista_server"
SUB_QUEUE_URl="https://sqs.ap-northeast-2.amazonaws.com/924873670641/regista_server_sub"

SERVER_QUEUE="server"
HANDLER_QUEUE="handler"




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
        logger = logging.getLogger("run")

        """
        Send task queue to celery broker
        """

        conn = MySQLClient()
        conn.init(**debug.MYSQL_CONFIG)
        schedule = Schedule(conn)

        while True:
            # get finished jobs
            data = conn.fetchall(
                """
                SELECT task_id, jid from job_schedule where task_id IS NOT NULL;
                """
            )
            
            # update job_status and task_id=NULL
            try:
                for row in data:
                    result = app.AsyncResult(row[0])
                    if result.state == "PENDING":
                        conn.execute(
                            f"""
                            update job_schedule set job_status=-999, task_id=NULL where jid={row[1]};
                            """
                        )
                    elif result.ready():
                        result_code = result.get()
                        if result_code == 0:
                            result_code = 99
                        else:
                            result_code = -result_code
                        print (result_code)
                        conn.execute(
                            f"""
                            update job_schedule set job_status={result_code}, task_id=NULL where jid={row[1]};
                            """
                        )
                conn.commit()
            except Exception as e:
                print (e)
                conn.rollback()

            # assign jobs
            jobs = schedule.get_assignable_jobs()
            print (jobs)
            try:
                for row in jobs:
                    logger.info(f"assign job: {row[1]}")
                    task_id = script.delay(row[1])
                    conn.execute(
                        f"""
                        update job_schedule set job_status=1, task_id='{task_id}', run_count=run_count+1 where jid={row[0]};
                        """
                    )
                conn.commit()
            except Exception as e:
                print (e)
                conn.rollback()
            
            logger.info("Sleep 5 secs...")
            time.sleep(5)


if __name__ == "__main__":
    print ("start")
    init_logger("run")
    server = Server("debug")
    server.send_task()

            
