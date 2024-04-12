from browser_control.axiom_driver import AxiomDriver
from database_sqlite.database import DatabaseManager

from multiprocessing import Process


def run_axiom_driver(uri: str, mode: str, stt: str, src: str| int):
    """
    Run the AxiomDriver in a separate process
    :param uri: uri for the database
    :param mode: "prod" or "test"
    :param stt: "Verify" or "Error"
    :param src: numeric key for the Source
    :return: None
    """
    stt = stt.capitalize()
    db_manager = DatabaseManager(uri)
    AxiomDriver(db_manager, mode, src, stt)


if __name__ == '__main__':
    source = "601"  # prospect
    run_mode = "prod"  # 'test' or 'prod'
    statuses = ["Verify"]  # must be a list
    db_uri = "sqlite:///database_sqlite/database.db"
    processes = []
    for status in statuses:
        p = Process(target=run_axiom_driver, args=(
            db_uri, run_mode, status, source))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()
