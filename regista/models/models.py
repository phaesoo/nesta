from sqlalchemy import Table, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from regista.models import Base


job_dependency = Table(
    "job_dependency",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("predecessor_job_id", Integer, ForeignKey("job.id")),
    Column("successor_job_id", Integer, ForeignKey("job.id"))
)


class Job(Base):
    """
    id: job id
    name: job name
    type: job type
    queue: queue name (celery)
    author: author name
    cron: cron synctax
    max_run_count: maxinum job run count
    """

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    queue = Column(String)
    author = Column(String, nullable=False)
    cron = Column(String)
    max_run_count = Column(Integer, nullable=False)

    # relationships
    job_schedule = relationship("JobSchedule", uselist=False, back_populates="job")
    job_schedule_hist = relationship("JobScheduleHist", uselist=False, back_populates="job")
    predecessors = relationship(
        "Job", secondary=job_dependency,
        primaryjoin=("Job.id==job_dependency.c.predecessor_job_id"),
        secondaryjoin=("Job.id==job_dependency.c.successor_job_id"),
        backref=backref("successors", lazy="dynamic"),
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<id>: {self.id}"


class JobSchedule(Base):
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    status = Column(Integer, default=0)
    scheduled_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    run_count = Column(Integer, default=0)
    max_run_count = Column(Integer, nullable=False)

    # relationships
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    job = relationship("Job", back_populates="job_schedule")


class JobScheduleHist(Base):
    """
    job schedule history table
    """
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    status = Column(Integer, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    run_count = Column(Integer, nullable=False)

    # relationships
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    job = relationship("Job", back_populates="job_schedule_hist")