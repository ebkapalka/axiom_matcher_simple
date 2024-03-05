from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class AxiomEvent(Base):
    """
    Model to store individual Axiom events
    """
    __tablename__ = 'error_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
