import re
from sqlalchemy.ext.declarative import declared_attr, declarative_base

class Base:
    @declared_attr
    def __tablename__(cls):
        """
        camel case to snake case
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

Base = declarative_base(cls=Base)