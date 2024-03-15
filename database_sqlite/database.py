from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, func, event
from datetime import timedelta

from database_sqlite.models import Base, AxiomEvent, URL


class DatabaseManager:
    def __init__(self, uri: str):
        self.engine = create_engine(uri, echo=False)

        # Ensure WAL mode is set for SQLite databases
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """
            Set the SQLite PRAGMA journal_mode to WAL
            :param dbapi_connection: database connection
            :param connection_record: record of the connection
            :return: None
            """
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.close()

        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine)

    def get_session(self) -> Session:
        """
        Get a session from the database
        :return: Session object
        """
        return self.SessionLocal()

    def add_event(self, event_type: str):
        """
        Add an event to the database
        :param event_type: type of event
        :return: None
        """
        with self.get_session() as session:
            new_event = AxiomEvent(event_type=event_type)
            session.add(new_event)
            session.commit()

    def check_out_url(self) -> URL:
        """
        Atomically check out a URL that hasn't been checked out or processed.
        :return: URL object or None if no URL is available.
        """
        session = self.get_session()
        try:
            # Start a transaction
            session.begin()
            url = session.query(URL).filter_by(is_checked_out=False, is_processed=False).with_for_update().first()
            if url:
                url.is_checked_out = True
                session.commit()  # Commit the transaction
                return url
        except Exception as e:
            session.rollback()  # Ensure to rollback in case of any exception
            print(type(e), e)
        finally:
            session.close()  # Ensure the session is closed after operation
        return None

    def mark_url_as_processed(self, url_str: str):
        """
        Mark a URL as processed and no longer checked out.
        :param url_str: The URL string to mark as processed.
        :return: None
        """
        session = self.get_session()
        try:
            session.begin()
            url_obj = session.query(URL).filter_by(url=url_str).one()
            url_obj.is_processed = True
            url_obj.is_checked_out = False
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error marking URL as processed: {e}")
        finally:
            session.close()

    def reset_checked_out_urls(self):
        """
        Reset the is_checked_out flag for all URLs, marking them as not checked out.
        This is useful for cleanup purposes, e.g., at startup or shutdown.
        """
        session = self.get_session()
        try:
            session.begin()
            # Update all rows where is_checked_out is True
            session.query(URL).filter_by(is_checked_out=True).update({"is_checked_out": False})
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error resetting checked out URLs: {e}")
        finally:
            session.close()

    def print_stats(self, time_thresh=timedelta(minutes=1)):
        """
        Print the statistics of the BannerDriver
        :return:
        """
        with self.get_session() as session:
            # Print the number of each type of event
            event_counts = session.query(
                AxiomEvent.event_type,
                func.count(AxiomEvent.event_type).label('count')
            ).group_by(AxiomEvent.event_type).all()
            if event_counts:
                print("\nEvent Statistics:")
                for event_type, count in event_counts:
                    print(f"    {event_type}: {count}")

            # New functionality to calculate processed records per hour
            processed_types = ["new record", "matched record", "deleted record"]  # "skip" is deliberately excluded
            processed_records = (session.query(AxiomEvent.timestamp).
                                 filter(AxiomEvent.event_type.in_(processed_types)).
                                 order_by(AxiomEvent.timestamp.desc()).all())

            # Find the first gap of more time_thresh between records
            for i in range(len(processed_records) - 1):
                if processed_records[i].timestamp - processed_records[i + 1].timestamp > time_thresh:
                    processed_records = processed_records[:i + 1]
                    break

            # Calculate the number of records processed per hour and minute
            if processed_records:
                start_time = processed_records[-1].timestamp
                end_time = processed_records[0].timestamp
                total_hours = (end_time - start_time).total_seconds() / 3600.0
                processed_per_hour = len(processed_records) / total_hours if total_hours > 0 else 0
                processed_per_minute = processed_per_hour / 60
                print(f"Processed Records Per Hour: ~{processed_per_hour:.2f}")
                print(f"Processed Records Per Minute: ~{processed_per_minute:.2f}")
                print(f"Seconds per Record: ~{60 / processed_per_minute:.5f}")
                print(f"Total Hours Last Run: {total_hours:.2f}")
