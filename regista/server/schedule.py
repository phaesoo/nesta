import logging
from croniter import croniter
from datetime import datetime, timedelta

from regista.configs import debug
from regista.models.models import Job, JobSchedule, JobScheduleHist
from regista.utils.mysql import MySQLClient


logger = logging.getLogger("run")


class Schedule:
    def __init__(self):
        self._conn = MySQLClient()
        self._conn.init(**debug.MYSQL_CONFIG)

    def insert(self, date):
        try:
            self._dump()
            self._insert(date)
            self._conn.commit()
        except Exception as e:
            logger.error(e)
            self._conn.rollback()
            print ("rollback()")

    def get_assignable_jobs(self):
        data = self._conn.fetchall(
            """
            SELECT a.jid, a.job_name from job a join job_schedule b on a.jid = b.jid
            WHERE (scheduled_time IS NULL or scheduled_time < NOW())
            AND b.job_status<>99
            AND a.jid NOT IN (SELECT DISTINCT a.jid FROM job_dependency a JOIN job_schedule b ON a.dependent_jid = b.jid WHERE job_status<>99)
            """
        )
        return data

    def _dump(self):
        """
        dump job_schedule > job_schedule_hist
        empty job_schedule
        """
        # dump job_schedule > job_schedule_hist
        data = self._conn.fetchall(
            """
            SELECT jid, job_date, job_status, start_time, end_time, run_count
            FROM job_schedule
            """
        )

        self._conn.executemany(
            """
            INSERT INTO job_schedule_hist (jid, job_date, job_status, start_time, end_time, run_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, data
        )

        self._conn.execute("DELETE FROM job_schedule")

    def _insert(self, date):
        """
        insert job_schedule table with job table 
        """
        target_dt = datetime(int(date[:4]), int(date[4:6]), int(date[6:8]))
        cutoff_dt = target_dt + timedelta(days=1)

        data = self._conn.fetchall(
            """
            SELECT jid, job_name, cron, max_run_count
            FROM job
            """
        )

        values = list()
        for row in data:
            cron = row[2]

            scheduled_time = None
            if cron:
                scheduled_time = croniter(row[2], target_dt).get_next(datetime)
                print (cutoff_dt, scheduled_time)
                if cutoff_dt < scheduled_time:
                    logger.info(
                        f"Skip scheduled_time > cutoff: id: {row[0]} name: {row[1]}")
                    continue
                
            values.append((row[0], target_dt.date(), scheduled_time, row[3]))

        print (values)
        self._conn.executemany(
            """
            INSERT INTO job_schedule (jid, job_date, scheduled_time, max_run_count)
            VALUES (%s, %s, %s, %s)
            """, values
        )

