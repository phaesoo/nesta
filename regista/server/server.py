import time
import pickle
import logging
from threading import Thread
from .define import define
from .schedule import Schedule
from regista.tasks.tasks import app, script
from regista.utils.rabbitmq import RabbitMQClient
from regista.configs import debug
from regista.utils.mysql import MySQLClient
from regista.utils.log import init_logger


class Server:
    def __init__(self, mode):
        self._mode = mode
        self._queue = RabbitMQClient()
        self._queue.init(
            host="localhost",
            port=5672,
            username="test",
            password="test",
            virtual_host="regista_server"
        )
        self._queue.queue_declare("server")
        self._queue.queue_declare("handler")

        self._is_run = False

    def run(self):
        logger = logging.getLogger("run")

        while True:
            # main queue has high priority
            result = self._queue.get("server")
            if result:
                logger.info(result)
                data = result["data"]

                cmd = data.get("command", None)
                by = data.get("by", "undefined")
                if cmd == "terminate":
                    logger.warn(f"Server is terminated by {by}")
                    break
                elif cmd == "stop":
                    self._is_run = False
                    logger.warn(f"Server is stopped by {by}")
                elif cmd == "resume":
                    self._is_run = True
                    logger.warn(f"Server is resumed by {by}")
                else:
                    logger.warn(f"Undefined server command {by}: {cmd}")
                continue
            
            if not self._is_run:
                logger.warn("Server has been stopped. sleep 5 sec")
                time.sleep(5)
                continue

            # sub queue has lower priority
            result = self._queue.get("handler")
            if result is None:
                time.sleep(1)
                logger.warn("Empty handler. sleep 1 sec")
                continue
            else:
                logger.info(f"result: {result}")

            title = result["title"]
            body = result["body"]

            if title == "result":
                pass
            else:
                print (f"Unknown title: {title}")
            
            logger.info("final sleep")
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
            if self._is_run is False:
                logger.warn("Server has been stopped. sleep 5 sec")
                time.sleep(5)
                continue

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

    t = Thread(target=server.send_task)
    t.start()
    t.join()

    print("Sleep 5 secs...")
