import logging
from croniter import croniter
from datetime import datetime, timedelta


logger = logging.getLogger("server")


def dump_schedule_hist(conn):
    """
    dump job_schedule > job_schedule_hist
    empty job_schedule
    """
    # dump job_schedule > job_schedule_hist
    data = conn.fetchall(
        """
        SELECT jid, job_date, job_status, assign_time, start_time, end_time, run_count
        FROM job_schedule
        """
    )

    conn.executemany(
        """
        INSERT INTO job_schedule_hist (jid, job_date, job_status, assign_time, start_time, end_time, run_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data
    )

    conn.execute("DELETE FROM job_schedule")


def generate_schedule(conn, date):
    """
    generate job_schedule table with job table 
    """
    target_dt = datetime(int(date[:4]), int(date[4:6]), int(date[6:8]))
    cutoff_dt = target_dt + timedelta(days=1)

    data = conn.fetchall(
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
            print(cutoff_dt, scheduled_time)
            if cutoff_dt < scheduled_time:
                logger.warn(
                    f"Skip scheduled_time > cutoff: id: {row[0]} name: {row[1]}")
                continue

        values.append((row[0], target_dt.date(), scheduled_time, row[3]))

    conn.executemany(
        """
        INSERT INTO job_schedule (jid, job_date, scheduled_time, max_run_count)
        VALUES (%s, %s, %s, %s)
        """, values
    )


def get_assignable_jobs(conn):
    return conn.fetchall(
        """
        SELECT a.jid, a.job_name from job a join job_schedule b on a.jid = b.jid
        WHERE (scheduled_time IS NULL or scheduled_time < NOW())
        AND b.job_status=0
        AND b.run_count < b.max_run_count
        AND a.jid NOT IN (SELECT DISTINCT a.jid FROM job_dependency a JOIN job_schedule b ON a.dependent_jid = b.jid WHERE job_status<>99)
        """
    )
