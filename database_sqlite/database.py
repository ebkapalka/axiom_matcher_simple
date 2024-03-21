from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, func, event
from datetime import timedelta

from database_sqlite.models import Base, AxiomEvent, URL


class DatabaseManager:
    def __init__(self, uri: str, worker_name: str):
        self.worker_name = worker_name
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

    def bulk_add_urls(self, url_list):
        """
        Bulk add URLs to the database, skipping URLs that already exist.
        :param url_list: A list of URL strings to be added.
        """
        session = self.get_session()
        try:
            existing_urls = session.query(URL.url).filter(URL.url.in_(url_list)).all()
            existing_urls_set = {url[0] for url in existing_urls}
            new_urls = [URL(url=url) for url in url_list if url not in existing_urls_set]
            if new_urls:
                session.add_all(new_urls)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding URLs: {e}")
        finally:
            session.close()

    def check_out_url(self) -> str | None:
        """
        Atomically check out a URL that hasn't been checked out or processed,
        assigning it to the specified worker.
        :param worker_name: The identifier of the worker checking out the URL.
        :return: URL object or None if no URL is available.
        """
        session = self.get_session()
        try:
            session.begin()
            url = session.query(URL).filter_by(checked_out_by=None,
                                               processed_by=None).first()
            if url:
                url.checked_out_by = self.worker_name
                session.commit()
                return url.url
        except Exception as e:
            session.rollback()
            print(type(e), e)
        finally:
            session.close()
        return None

    def mark_url_as_processed(self, url_str: str):
        """
        Mark a URL as processed, clearing the worker assignment.
        :param worker_name: The identifier of the worker processing the URL.
        :param url_str: The URL string to mark as processed.
        :return: None
        """
        session = self.get_session()
        try:
            session.begin()
            url_obj = session.query(URL).filter_by(url=url_str).one()
            url_obj.processed_by = self.worker_name
            url_obj.checked_out_by = None
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error marking URL as processed: {e}")
        finally:
            session.close()

    def reset_checked_out_urls(self):
        """
        Reset the checked_out_by field for all URLs, marking them as not checked out.
        This is useful for cleanup purposes, e.g., at startup or shutdown.
        """
        session = self.get_session()
        try:
            session.begin()
            session.query(URL).filter(URL.checked_out_by.is_not(
                None)).update({"checked_out_by": None})
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
                total_seconds = (end_time - start_time).total_seconds()
                total_hours = total_seconds / 3600.0
                processed_per_hour = len(processed_records) / total_hours if total_hours > 0 else 0
                processed_per_minute = processed_per_hour / 60 if processed_per_hour > 0 else 0
                seconds_per_record = 60 / processed_per_minute if processed_per_minute > 0 else float('inf')
                print(f"Processed Records Per Hour: ~{processed_per_hour:.2f}")
                print(f"Processed Records Per Minute: ~{processed_per_minute:.2f}")
                print(f"Seconds per Record: ~{seconds_per_record:.5f}")
                print(f"Total Hours Last Run: {total_hours:.2f}")
