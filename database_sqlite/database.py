from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, func
import atexit

from models import Base, AxiomEvent

class DatabaseManager:
    def __init__(self, uri: str):
        self.engine = create_engine(uri, echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine)
        atexit.register(self.print_stats)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def add_event(self, event_type: str):
        with self.get_session() as session:
            new_event = AxiomEvent(event_type=event_type)
            session.add(new_event)
            session.commit()

    def print_stats(self):
        """
        Print the statistics of the BannerDriver
        :return:
        """
        with self.get_session() as session:
            event_counts = session.query(
                AxiomEvent.event_type,
                func.count(AxiomEvent.event_type).label('count')
            ).group_by(AxiomEvent.event_type).all()

            print("Event Statistics:")
            for event_type, count in event_counts:
                print(f"{event_type}: {count}")
