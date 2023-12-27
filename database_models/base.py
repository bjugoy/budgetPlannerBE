import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

#muss ich angeblich löschen
#from main import session


Base = declarative_base()
#Base.query = session.query_property()

class TimeStampedModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, onupdate=datetime.datetime.now(datetime.UTC))