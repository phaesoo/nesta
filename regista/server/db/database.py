from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


__sessions = dict()
__engines = dict()


def init_db():
    database = "test.db"
    db_name = "prod"
    engine = create_engine("sqlite:///{}".format(database), echo=False)
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    # import models
    from regista.models import Base
    from regista.models.models import Job, JobSchedule

    Base.query = session.query_property()
    Base.metadata.create_all(engine)

    __sessions[db_name] = session
    __engines[db_name] = engine


def get_session(db_name):
    session = __sessions.get(db_name)
    if session is None:
        raise ValueError(f"Undefined DB Name: {db_name}")
    return session


def get_engine(db_name):
    engine = __engines.get(db_name)
    if engine is None:
        raise ValueError(f"Undefined DB Name: {db_name}")
    return engine