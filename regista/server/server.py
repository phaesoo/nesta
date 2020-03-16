import time
import pickle
import logging
from threading import Thread
from .define import define
from .schedule import Schedule
from regista.tasks.tasks import app, script
from regista.utils.rabbitmq import RabbitMQClient
from regista.utils.mysql import MySQLClient
from regista.utils.log import init_logger


class Server:
    def __init__(self, configs):
        assert isinstance(configs, dict)

        self._config_common = configs["services"]["common"]
        self._config_server = configs["services"]["server"]

        self._conn = MySQLClient()
        self._conn.init(**self._config_common["mysql"])

        self._is_run = self._config_server.get("auto_start", False)
        self._is_exit = False

    def run(self):
        logger = logging.getLogger("run")

        mq_client = RabbitMQClient()
        mq_client.init(**self._config_common["rabbitmq"])

        queues = self._config_common["rabbitmq"]["queues"]
        assert isinstance(queues, list)
        assert len(queues) == 2
        for queue in queues:
            # delete existing queue and declare before starting
            mq_client.queue_delete(queue)
            mq_client.queue_declare(queue)

        while True:
            if self._is_exit:
                break

            # main queue has high priority
            result = mq_client.get(queues[0])
            if result:
                logger.info(result)
                self._handle_queue(result["data"])
                continue
            
            if not self._is_run:
                logger.warn("Server has been stopped. sleep 5 sec")
                time.sleep(5)
                continue

            # assign jobs
            self._assign_jobs()
            
            logger.info("final sleep")
            time.sleep(1)

    def _handle_queue(self, data):
        title = data["title"]
        body = data["body"]

        if title == "server":
            cmd = body.get("command", None)
            by = body.get("by", "undefined")
            if cmd == "terminate":
                print(f"Server is terminated by {by}")
                self._is_exit = True
            elif cmd == "stop":
                self._is_run = False
                print(f"Server is stopped by {by}")
            elif cmd == "resume":
                self._is_run = True
                print(f"Server is resumed by {by}")
            else:
                print(f"Undefined {title} command {by}: {cmd}")
        elif title == "schedule":
            cmd = body.get("command", None)
            if cmd == "insert":
                schedule = Schedule(self._conn)
                schedule.insert(20200314)
            else:
                print(f"Undefined {title} command {by}: {cmd}")

    def _assign_jobs(self):
        schedule = Schedule(self._conn)
        # assign jobs
        jobs = schedule.get_assignable_jobs()
        print (jobs)
        try:
            for row in jobs:
                print(f"assign job: {row[1]}")
                task_id = script.delay(row[1])
                self._conn.execute(
                    f"""
                    update job_schedule set job_status=1, task_id='{task_id}', run_count=run_count+1 where jid={row[0]};
                    """
                )
            self._conn.commit()
        except Exception as e:
            print (e)
            self._conn.rollback()

    def update_result(self):
        logger = logging.getLogger("run")
        """
        Send task queue to celery broker
        """

        while True:
            if self._is_exit is True:
                logger.warn(f"update_result is terminated")
                break
            if self._is_run is False:
                logger.warn("Server has been stopped. sleep 5 sec")
                time.sleep(5)
                continue

            # get finished jobs
            data = self._conn.fetchall(
                """
                SELECT task_id, jid from job_schedule where task_id IS NOT NULL;
                """
            )
            
            # update job_status and task_id=NULL
            try:
                for row in data:
                    result = app.AsyncResult(row[0])
                    if result.state == "PENDING":
                        self._conn.execute(
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
                        self._conn.execute(
                            f"""
                            update job_schedule set job_status={result_code}, task_id=NULL where jid={row[1]};
                            """
                        )
                self._conn.commit()
            except Exception as e:
                print (e)
                self._conn.rollback()
            
            logger.info("Sleep 5 secs...")
            time.sleep(5)
