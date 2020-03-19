import os
import logging
import socket
import time
import pickle
from threading import Thread
from .define import define
from . import schedule
from regista.external.daemon import Daemon
from regista.tasks.tasks import get_app
from regista.utils.rabbitmq import RabbitMQClient
from regista.utils.mysql import MySQLClient


logger = logging.getLogger("server")


class Server(Daemon):
    def __init__(self, configs):
        assert isinstance(configs, dict)

        self._config_common = configs["services"]["common"]
        self._config_server = configs["services"]["server"]

        pidfile = os.path.join(configs["ROOT_DIR"], "server.pid")
        daemon_log = os.path.join(configs["ROOT_DIR"], "daemon.log")

        super().__init__(
            pidfile=pidfile,
            stdout=daemon_log,
            stderr=daemon_log
            )

        self._app = get_app(**self._config_common["celery"])

        self._conn = MySQLClient()
        self._conn.init(**self._config_common["mysql"])

        self._interval = self._config_server["interval"]
        self._is_run = self._config_server["auto_start"]
        self._is_exit = False

    def run(self):
        logger.info("Server has been started")
        threads = [Thread(target=t) for t in [self._health_check, self._update_result]]

        for t in threads:
            t.start()

        self._main()

        for t in threads:
            t.join()
        logger.info("Server has been terminated")

    def _health_check(self):
        """
        thread for server health check
        """
        logger.info("Health check started")

        # prepare for server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(
            (self._config_server["host"], self._config_server["port"]))
        server_socket.listen()
        server_socket.settimeout(0.5)

        while True:
            if self._is_exit:
                break
            try:
                client_socket, _ = server_socket.accept()
                msg = client_socket.recv(1024).decode()
                if msg == "hi":
                    client_socket.sendall("hello".encode())
            except socket.timeout:
                pass
            except Exception as e:
                logger.error(f"health_check error: {e}")

        client_socket.close()
        server_socket.close()

    def _main(self):
        """
        main thread for handling message queues and assigning jobs
        """
        mq_client = RabbitMQClient()
        mq_client.init(**self._config_common["rabbitmq"])

        queue = self._config_common["rabbitmq"]["queue"]
        # purge and declare before starting
        try:
            pass
            #mq_client.queue_purge(queue)
        except:
            pass
        mq_client.queue_declare(queue)

        is_first = True

        while True:
            if self._is_exit:
                break

            # imte interval from second loop
            if is_first is True:
                is_first = False
            else:
                time.sleep(self._interval)

            # main queue has high priority
            data = mq_client.get(queue)
            if data:
                logger.info(data)
                try:
                    self._handle_queue(data)
                except Exception as e:
                    logger.error(f"Error while _handle_queue: {e}")
                continue

            if not self._is_run:
                logger.info("Server has been stopped")
                continue

            # assign jobs
            self._assign_jobs()

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
                schedule.insert_schedule(self._conn, body["date"])
            else:
                logger.warn(f"Undefined {title} command {by}: {cmd}")
        else:
            raise ValueError(f"Undefined title: {title}")

    def _assign_jobs(self):
        # assign jobs
        jobs = schedule.get_assignable_jobs(self._conn)
        if not len(jobs):
            logger.info("There is no assignable jobs")
            return

        logger.info(jobs)
        try:
            for row in jobs:
                logger.info(f"assign job: {row[1]}")
                task_id = self._app.send_task("script", [row[1]])
                self._conn.execute(
                    f"""
                    update job_schedule set job_status=1, task_id='{task_id}', run_count=run_count+1 where jid={row[0]};
                    """
                )
            self._conn.commit()
        except Exception as e:
            logger.error(e)
            self._conn.rollback()

    def _update_result(self):
        """
        thread for updating result
        """

        is_first = True

        while True:
            # imte interval from second loop
            if is_first is True:
                is_first = False
            else:
                time.sleep(self._interval)

            if self._is_exit is True:
                logger.warn(f"update_result is terminated")
                break
            if self._is_run is False:
                logger.info("Server has been stopped")
                continue

            # get finished jobs
            data = self._conn.fetchall(
                """
                SELECT task_id, jid from job_schedule where task_id IS NOT NULL;
                """
            )
            if not len(data):
                logger.info("No data to update result")
                continue

            # update job_status and task_id=NULL
            try:
                for row in data:
                    result = self._app.AsyncResult(row[0])
                    print (result.state)
                    if result.state == "PENDING":
                        self._conn.execute(
                            f"""
                            UPDATE job_schedule SET job_status=-999, task_id=NULL where jid={row[1]};
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
                logger.error(e)
                self._conn.rollback()
