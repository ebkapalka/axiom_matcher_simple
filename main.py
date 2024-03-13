from browser_control.axiom_driver import AxiomDriver
from database_sqlite.database import DatabaseManager

if __name__ == '__main__':
    run_mode = "prod"
    option = "error"
    # TODO: add option to pick a different verifier tile
    db_uri = "sqlite:///database_sqlite/database.db"
    db_manager = DatabaseManager(db_uri)
    driver = AxiomDriver(db_manager,
                         run_mode,
                         option)
