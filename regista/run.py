import os
import sys
from croniter import croniter
from datetime import datetime
from regista.server.db.database import init_db, get_session
from regista.models.models import Job
from regista.server.schedule import Schedule
from regista.utils.log import init_logger


if __name__ == "__main__":
    init_logger("run")

    schedule = Schedule()
    #schedule.insert("20200302")
    assignable_jobs = schedule.get_assignable_jobs()
    print (assignable_jobs)
