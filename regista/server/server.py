import logging
import socket
import time
import pickle
from threading import Thread
from .define import define
from .schedule import Schedule
from regista.tasks.tasks import app, script
from regista.utils.rabbitmq import RabbitMQClient
from regista.utils.mysql import MySQLClient
from regista.utils.log import init_logger


logger = logging.getLogger("server")


class Server:
    def __init__(self, configs):
        assert isinstance(configs, dict)

        self._config_common = configs["services"]["common"]
        self._config_server = configs["services"]["server"]

        self._conn = MySQLClient()
        self._conn.init(**self._config_common["mysql"])

        self._is_run = self._config_server.get("auto_start", False)
        self._is_exit = False

    def health_check(self):
        logger.info("Health check started")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("localhost", 9999))
        server_socket.listen()

        while True:
            client_socket, addr = server_socket.accept()
            logger.warn(client_socket.recv(1024).decode(), addr)
            client_socket.sendall("hello".encode())

        client_socket.close()
        server_socket.close()

    def run(self):
        mq_client = RabbitMQClient()
        mq_client.init(**self._config_common["rabbitmq"])

        queue = self._config_common["rabbitmq"]["queue"]
        # purge and declare before starting
        mq_client.queue_purge(queue)
        mq_client.queue_declare(queue)

        while True:
            if self._is_exit:
                break

            # main queue has high priority
            data = mq_client.get(queue)
            if data:
                logger.info(data)
                self._handle_queue(data)
                continue
            
            if not self._is_run:
                logger.info("Server has been stopped. sleep 5 sec")
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
                logger.warn(f"Server is terminated by {by}")
                self._is_exit = True
            elif cmd == "stop":
                self._is_run = False
                logger.warn(f"Server is stopped by {by}")
            elif cmd == "resume":
                self._is_run = True
                logger.warn(f"Server is resumed by {by}")
            else:
                logger.warn(f"Undefined {title} command {by}: {cmd}")
        elif title == "schedule":
            cmd = body.get("command", None)
            if cmd == "insert":
                schedule = Schedule(self._conn)
                schedule.insert(20200314)
            else:
                logger.warn(f"Undefined {title} command {by}: {cmd}")

    def _assign_jobs(self):
        schedule = Schedule(self._conn)
        # assign jobs
        jobs = schedule.get_assignable_jobs()
        logger.info(jobs)
        try:
            for row in jobs:
                logger.info(f"assign job: {row[1]}")
                task_id = script.delay(row[1])
                self._conn.execute(
                    f"""
                    update job_schedule set job_status=1, task_id='{task_id}', run_count=run_count+1 where jid={row[0]};
                    """
                )
            self._conn.commit()
        except Exception as e:
            logger.warn(e)
            self._conn.rollback()

    def update_result(self):
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
                        self._conn.execute(
                            f"""
                            update job_schedule set job_status={result_code}, task_id=NULL where jid={row[1]};
                            """
                        )
                self._conn.commit()
            except Exception as e:
                logger.warn(e)
                self._conn.rollback()
            
            logger.info("Sleep 5 secs...")
            time.sleep(5)
