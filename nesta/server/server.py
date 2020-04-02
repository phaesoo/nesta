import os
import logging
import socket
import time
import pickle
from argparse import ArgumentParser
from threading import Thread, Lock
from nesta.server.define import define
from nesta.server import schedule
from nesta.external.daemon import Daemon
from nesta.tasks.tasks import get_worker
from nesta.tasks.notice import get_notice
from nesta.utils.rabbitmq import RabbitMQClient
from nesta.utils.mysql import MySQLClient
from nesta.utils.log import init_logger
from nesta.configs.util import parse_env, parse_config, get_defined_path


def parse_arguments():
    parser = ArgumentParser("Nesta server")
    parser.add_argument("--daemonize", "-d", dest="daemonize",
                        type=bool, default=True, help="daemonize or not")
    return parser.parse_args()


class Server(Daemon):
    def __init__(self, configs):
        assert isinstance(configs, dict)

        self._config_common = configs["services"]["common"]
        self._config_server = configs["services"]["server"]

        log_path = get_defined_path(
            configs["services"]["server"]["log_path"], configs["env"])

        pidfile = os.path.join(log_path, "server.pid")
        daemon_log = os.path.join(log_path, "daemon.log")

        super().__init__(
            pidfile=pidfile,
            stdout=daemon_log,
            stderr=daemon_log
        )

        self._logger = init_logger(
            log_path, "server", configs["services"]["server"]["log_level"])

        self._worker = get_worker(**configs)
        self._notice = get_notice(**configs)

        self._interval = self._config_server["interval"]
        self._status = define.STATUS_RUNNING if self._config_server[
            "auto_start"] else define.STATUS_STOPPED

        self._mutex = Lock()

    def _run(self):
        self._logger.info("Server has been started")
        self._notice.send_task(
            "notice",
            kwargs={
                "level": "INFO",
                "msg": "Server has been started"
            })
        threads = [Thread(target=self._wrap, args=[func])
                   for func in [self._communicate, self._update_result]]

        for t in threads:
            t.start()

        self._main()
        """
        try:
            self._wrap(self._main)
        except Exception as e:
            print (e)
        """
        for t in threads:
            t.join()

        self._notice.send_task(
            "notice", 
            kwargs={
                "level": "CRITICAL",
                "msg": "Server has been terminated"
            })
        self._logger.info("Server has been terminated")

    def _set_status(self, status):
        with self._mutex:
            self._status = status

    def _wrap(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            self._status = define.STATUS_TERMINATED
            self._logger.critical(f"Unexpected error, start to terminate :{e}")
            self._notice.send_task(
                "notice",
                kwargs={
                    "level": "CRITICAL",
                    "msg" : "Unexpected error, start to terminate: {}".format(e)
                })

    def _communicate(self):
        """
        thread for communicating with external clients(control)
        """
        self._logger.debug("communicate thread has been started")

        # prepare for server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(
            (self._config_server["host"], self._config_server["port"]))
        server_socket.listen()
        server_socket.settimeout(0.5)

        while True:
            if self._status == define.STATUS_TERMINATED:
                self._logger.debug("communicate thread has been terminated")
                break
            try:
                client_socket, _ = server_socket.accept()
                msg = client_socket.recv(1024).decode()
                self._logger.info("Recieve msg from client: {}".format(msg))
                if msg == "hi":
                    client_socket.sendall("hello".encode())
                elif msg == "status":
                    client_socket.sendall(self._status.encode())
                else:
                    self._logger.warn(f"Unknown msg: {msg}")
                client_socket.close()
            except socket.timeout:
                pass
            except Exception as e:
                self._logger.error(f"Unexpected error: {e}")
        server_socket.close()

    def _main(self):
        """
        main thread for handling message queues and assigning jobs
        """
        self._logger.debug("main thread has been started")

        conn = MySQLClient()
        conn.init(**self._config_common["mysql"])

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
            if self._status == define.STATUS_TERMINATED:
                self._logger.debug("main thread has been terminated")
                break

            # imte interval from second loop
            if is_first is True:
                is_first = False
            else:
                time.sleep(self._interval)

            data = mq_client.get(queue)
            if data:
                self._logger.info("Recieve queue: {}".format(data))
                try:
                    self._handle_queue(conn, data)
                except Exception as e:
                    self._logger.error(f"Error while _handle_queue: {e}")
                continue

            if self._status == define.STATUS_STOPPED:
                self._logger.info("Server has been stopped")
                continue

            # assign jobs
            self._assign_jobs(conn)

    def _handle_queue(self, conn, data):
        title = data["title"]
        body = data["body"]

        self._logger.debug(
            "handle_queue > title: {}, body: {}".format(title, body))
        self._notice.send_task(
            "notice", 
            kwargs={
                "level": "INFO",
                "msg": "handle_queue > title: {}, body: {}".format(title, body)}
                )

        if title == "server":
            cmd = body.get("command", None)
            by = body.get("by", "undefined")
            if cmd == "terminate":
                self._logger.info(f"Server is terminated by {by}")
                self._set_status(define.STATUS_TERMINATED)
            elif cmd == "stop":
                self._set_status(define.STATUS_STOPPED)
                self._logger.info(f"Server is stopped by {by}")
            elif cmd == "resume":
                self._set_status(define.STATUS_RUNNING)
                self._logger.info(f"Server is resumed by {by}")
            else:
                self._logger.info(f"Undefined {title} command {by}: {cmd}")
        elif title == "schedule":
            cmd = body.get("command", None)
            if cmd == "insert":
                date = body["date"]
                assert isinstance(date, str)
                try:
                    schedule.dump_schedule_hist(conn)
                    schedule.generate_schedule(conn, date)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    self._logger.error(
                        "Error while generating schedule: {}".format(e))
            else:
                self._logger.warn(f"Undefined {title} command: {cmd}")
        else:
            raise ValueError(f"Undefined title: {title}")

    def _assign_jobs(self, conn):
        # commit for getting up-to-date db status
        conn.commit()

        # assign jobs
        jobs = schedule.get_assignable_jobs(conn)
        if not len(jobs):
            self._logger.debug("There is no assignable jobs")
            return

        try:
            for row in jobs:
                self._logger.info(f"Assign job: {row[1]}")
                task_id = self._worker.send_task("script", [row[1]])
                conn.execute(
                    f"""
                    UPDATE job_schedule
                    SET job_status=1, task_id='{task_id}', run_count=run_count+1, assign_time=now()
                    WHERE jid={row[0]};
                    """
                )
            conn.commit()
        except Exception as e:
            self._logger.error(e)
            conn.rollback()
            self._notice.send_task(
                "notice",
                kwargs={
                    "level": "ERROR",
                    "msg": "Error while assign_jobs: {}".format(e)
                })

    def _update_result(self):
        """
        thread for updating result
        """
        self._logger.debug("update_result thread has been started")

        conn = MySQLClient()
        conn.init(**self._config_common["mysql"])

        is_first = True

        while True:
            # time interval from second loop
            if is_first is True:
                is_first = False
            else:
                time.sleep(self._interval)

            if self._status == define.STATUS_TERMINATED:
                self._logger.debug("update_result thread has been terminated")
                break
            elif self._status == define.STATUS_STOPPED:
                self._logger.debug("update_result thread has been stopped")
                continue

            # commit for getting up-to-date db status
            conn.commit()

            # get finished jobs
            data = conn.fetchall(
                """
                SELECT jid, task_id, job_status from job_schedule where task_id IS NOT NULL;
                """
            )
            if not len(data):
                self._logger.debug("No data to update result")
                continue

            # update job_status and task_id=NULL
            sql_list = list()
            for row in data:
                job_id = row[0]
                task_id = row[1]
                job_status = row[2]

                result = self._worker.AsyncResult(task_id)
                state = result.state
                self._logger.info("Result: state({}), jid({}), task_id({}), job_status({})".format(
                    state, job_id, task_id, job_status))

                if result.ready():
                    if state == "REVOKED":
                        sql_list.append("""
                            update job_schedule set job_status=-9, task_id=NULL where jid={};
                            """.format(job_id)
                        )
                    elif state in ["STARTED", "SUCCESS"]:
                        result_code = result.get()
                        if result_code == 0:
                            self._notice.send_task(
                                "notice",
                                kwargs={
                                    "level": "INFO",
                                    "msg": "Job finished: state({}), jid({}), task_id({}), job_status({})".format(
                                state, job_id, task_id, job_status)
                                })
                            result_code = 99
                        else:
                            self._notice.send_task(
                                "notice",
                                kwargs={
                                    "level": "ERROR", 
                                    "msg": "Result: state({}), jid({}), task_id({}), job_status({})".format(
                                state, job_id, task_id, job_status)
                                })
                            result_code = -result_code

                        sql_list.append("""
                            update job_schedule set job_status={}, task_id=NULL where jid={};
                            """.format(result_code, job_id)
                        )
                    elif state == "FAILURE":
                        self._notice.send_task(
                            "notice",
                            kwargs={
                                "level": "CRITICAL", 
                                "msg": "Result: state({}), jid({}), task_id({}), job_status({})".format(
                            state, job_id, task_id, job_status)
                            })
                        sql_list.append("""
                            update job_schedule set job_status=-999 and task_id=NULL where jid={};
                            """.format(job_id)
                        )
                    else:
                        self._logger.error(
                            "Unexpected ready status: {}".format(state))
                elif state == "STARTED":
                    if job_status == 1:
                        sql_list.append("""
                            update job_schedule set job_status=2 where jid={};
                            """.format(job_id)
                        )
                elif state == "PENDING":
                    continue
                elif state == "FAILURE":
                    self._notice.send_task(
                        "notice",
                        kwargs={
                            "level": "CRITICAL", 
                            "msg": "Result: state({}), jid({}), task_id({}), job_status({})".format(
                        state, job_id, task_id, job_status)
                        })
                    sql_list.append("""
                        update job_schedule set job_status=-999 and task_id=NULL where jid={};
                        """.format(job_id)
                    )
                else:
                    self._logger.error("Unexpected status: {}".format(state))
                    self._notice.send_task(
                        "notice",
                        kwargs={
                            "level": "CRITICAL",
                            "msg": "Result: state({}), jid({}), task_id({}), job_status({})".format(
                        state, job_id, task_id, job_status)
                        })

            # nothing to proceed
            if len(sql_list):
                self._logger.info("sql_list: {}".format(sql_list))
                try:
                    for sql in sql_list:
                        conn.execute(sql)
                    conn.commit()
                except Exception as e:
                    self._logger.error(e)
                    conn.rollback()


if __name__ == "__main__":
    env_dict = parse_env()
    configs = parse_config(env_dict["MODE"])
    configs["env"] = env_dict

    option = parse_arguments()

    server = Server(configs=configs)
    server.start()
