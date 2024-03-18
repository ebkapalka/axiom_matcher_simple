from browser_control.axiom_fetcher import AxiomFetcher
from browser_control.axiom_logindummy import AxiomDummy
from browser_control.axiom_worker import AxiomWorker
from database_sqlite.database import DatabaseManager

from multiprocessing import Process
import atexit

MAX_WORKERS = 12


def wrapup_db(config: dict):
    """
    Print the statistics of the database
    :param config: dictionary of configuration options
    :return: None
    """
    uri = config["database uri"]
    db_manager = DatabaseManager(uri, "wrapup")
    db_manager.reset_checked_out_urls()
    db_manager.print_stats()


def run_fetcher(config: dict, credentials: dict):
    """
    Run the AxiomFetcher in a separate process
    :param config: dictionary of configuration options
    :param credentials: dictionary of credentials
    :return: None
    """
    uri = config["database uri"]
    db_manager = DatabaseManager(uri, "fetcher")
    AxiomFetcher(db_manager, config, credentials)


def run_worker(config: dict, credentials: dict, worker_id: str):
    """
    Run the AxiomFetcher in a separate process
    :param config: dictionary of configuration options
    :param credentials: dictionary of credentials
    :param worker_id: identifier for the worker
    :return: None
    """
    uri = config["database uri"]
    worker_name = f"Worker - {worker_id}"
    db_manager = DatabaseManager(uri, worker_name)
    AxiomWorker(db_manager, config, credentials, worker_name)


def main(num_proc: int, config: dict):
    """
    Main function
    :return: None
    """
    if isinstance(config["issue types"], str):
        config["issue types"] = [config["issue types"]]
    num_proc = max(1, min(MAX_WORKERS, num_proc))

    uri = config["database uri"]
    db_resetter = DatabaseManager(uri, "")
    db_resetter.reset_checked_out_urls()
    cred_getter = AxiomDummy(config)
    creds = cred_getter.get_credentials()
    fetch_proc = Process(target=run_fetcher,args=(config, creds))
    fetch_proc.start()

    # start the processes
    worker_processes = []
    for worker_id in range(num_proc):
        worker_proc = Process(target=run_worker,
                              args=(config, creds, worker_id))
        worker_processes.append(worker_proc)
        worker_proc.start()

    # wait for the processes to finish
    for p in worker_processes:
        p.join()
    fetch_proc.join()


if __name__ == '__main__':
    num_processes = 4
    configuration = {
        "environment mode": "prod",  # "prod" or "test"
        "issue types": ["verify", "error"],  # "verify" or "error"
        "record type": "prospects",  # "prospects" or "act"
        "database uri": "sqlite:///database_sqlite/database.db"
    }
    atexit.register(wrapup_db, configuration)
    main(num_processes, configuration)
