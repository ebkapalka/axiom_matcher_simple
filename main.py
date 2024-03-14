from browser_control.axiom_driver import AxiomDriver
from database_sqlite.database import DatabaseManager

from multiprocessing import Process


def run_axiom_driver(uri: str, mode: str, opt: str):
    """
    Run the AxiomDriver in a separate process
    :param uri: uri for the database
    :param mode: "prod" or "test"
    :param option: "default" or "error"
    :return: None
    """
    db_manager = DatabaseManager(uri)
    AxiomDriver(db_manager, mode, opt)


if __name__ == '__main__':
    run_mode = "prod"
    options = ["default", "error"]
    db_uri = "sqlite:///database_sqlite/database.db"
    processes = []
    for option in options:
        p = Process(target=run_axiom_driver, args=(db_uri, run_mode, option))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()
