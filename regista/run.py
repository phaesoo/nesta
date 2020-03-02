import os
import sys
from croniter import croniter
from datetime import datetime
from regista.db.database import init_db, get_session
from regista.models.models import Job
from regista.server.schedule import Schedule
from regista.utils.log import init_logger


if __name__ == "__main__":
    init_logger("run")

    try:
        #os.remove("./test.db")
        pass
    except:
        pass

    init_db()
    session = get_session("prod")

    cron = "0 12 1-5 * *"
    if not croniter.is_valid(cron):
        raise ValueError("Invalid cron")

    try:
        job1 = Job(
            id=1,
            name="calendar",
            author="tom",
            type="DM",
            cron=cron,
            max_run_count=2
        )

        job2 = Job(
            id=2,
            name="universe",
            author="tom",
            type="DM",
            cron=cron,
            max_run_count=2
        )

        job3 = Job(
            id=3,
            name="sync",
            author="tom",
            type="DM",
            cron="0 12 * 5 *",
            max_run_count=2
        )

        job2.predecessors.append(job1)

        session.add(job1)
        session.add(job2)
        session.add(job3)
        session.commit()
    except:
        session.rollback()

    schedule = Schedule()
    schedule.insert("20200302")
