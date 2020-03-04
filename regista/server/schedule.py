import logging
from croniter import croniter
from datetime import datetime, timedelta
from regista.db.database import get_session
from regista.models.models import Job, JobSchedule, JobScheduleHist


logger = logging.getLogger("run")


class Schedule:
    def __init__(self):
        pass

    def insert(self, date):
        session = get_session("prod")
        try:
            self._dump(session)
            self._insert(session, date)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()

    def _dump(self, session):
        """
        dump job_schedule > job_schedule_hist
        empty job_schedule
        """
        # dump job_schedule > job_schedule_hist
        job_schedules = session.query(JobSchedule).all()

        objects = list()
        for job_schedule in job_schedules:
            objects.append(JobScheduleHist(
                date=job_schedule.date,
                status=job_schedule.status,
                start_time=job_schedule.start_time,
                end_time=job_schedule.end_time,
                run_count=job_schedule.run_count,
                job_id=job_schedule.job_id,
            ))
        session.bulk_save_objects(objects)

        # empty job_schedule
        session.query(JobSchedule).delete()

    def _insert(self, session, date):
        """
        insert job_schedule table with job table 
        """
        jobs = session.query(Job).all()

        target_dt = datetime(int(date[:4]), int(date[4:6]), int(date[6:8]))
        cutoff_dt = target_dt + timedelta(days=1)

        objects = list()
        for job in jobs:
            iter = croniter(job.cron, target_dt)
            scheduled_time = iter.get_next(datetime)
            if cutoff_dt < scheduled_time:
                logger.info(
                    f"Skip scheduled_time > cutoff: id: {job.id} name: {job.name}")
                continue
            objects.append(JobSchedule(
                date=target_dt.date(),
                scheduled_time=scheduled_time,
                max_run_count=job.max_run_count,
                job_id=job.id,
            ))
        session.bulk_save_objects(objects)
