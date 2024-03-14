from browser_control.axiom_fetcher import AxiomFetcher
from browser_control.axiom_worker import AxiomWorker
from database_sqlite.database import DatabaseManager

from multiprocessing import Process, Manager, Lock, Event
import atexit


def wrapup_db(config: dict):
    """
    Print the statistics of the database
    :param config: dictionary of configuration options
    :return: None
    """
    uri = config["database uri"]
    db_manager = DatabaseManager(uri)
    db_manager.reset_checked_out_urls()
    db_manager.print_stats()


def run_fetcher(config: dict, credentials: dict, event_signal: Event):
    """
    Run the AxiomFetcher in a separate process
    :param config: dictionary of configuration options
    :param credentials: dictionary of credentials
    :param shared_urls: list of urls to process
    :param lock_obj: lock_obj for the shared_urls list
    :return: None
    """
    uri = config["database uri"]
    db_manager = DatabaseManager(uri)
    AxiomFetcher(db_manager, config, credentials, event_signal)


def run_worker(config: dict, credentials: dict):
    """
    Run the AxiomFetcher in a separate process
    :param config: dictionary of configuration options
    :param credentials: dictionary of credentials
    :param shared_urls: list of urls to process
    :param lock_obj: lock_obj for the shared_urls list
    :return: None
    """
    uri = config["database uri"]
    db_manager = DatabaseManager(uri)
    AxiomWorker(db_manager, config, credentials)


def main(num_proc: int, config: dict):
    """
    Main function
    :return: None
    """
    num_proc = max(1, min(10, num_proc))
    with Manager() as manager:
        creds = manager.dict()
        event = Event()
        fetch_proc = Process(target=run_fetcher,
                             args=(config, creds, event))
        fetch_proc.start()

        # start the processes
        worker_processes = []
        for _ in range(num_proc):
            worker_proc = Process(target=run_worker,
                                  args=(config, creds))
            worker_processes.append(worker_proc)
            worker_proc.start()
        fetch_proc.start()

        # wait for the processes to finish
        for p in worker_processes:
            p.join()
        fetch_proc.join()


if __name__ == '__main__':
    num_processes = 1
    configuration = {
        "environment mode": "prod",  # "prod" or "test"
        "issue type": "default",  # "default" or "error"
        "record type": "prospects",  # "prospects" or "act"
        "database uri": "sqlite:///database_sqlite/database.db"
    }
    atexit.register(wrapup_db, configuration)
    main(num_processes, configuration)
