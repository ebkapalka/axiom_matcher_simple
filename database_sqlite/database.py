from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, func
import atexit

from database_sqlite.models import Base, AxiomEvent

class DatabaseManager:
    def __init__(self, uri: str):
        self.engine = create_engine(uri, echo=False)
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
            if event_counts:
                print("\nEvent Statistics:")
                for event_type, count in event_counts:
                    print(f"    {event_type}: {count}")
