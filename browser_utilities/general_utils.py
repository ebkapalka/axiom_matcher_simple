import pwinput
import sys


REC_TYPES = {
    "prospects": 601,
    "act": 361,
    # add other record types here as needed
}


def generate_urls(config: dict) -> tuple[str, str, str]:
    """
    Generate the base URL and login URL
    :param config: configuration dictionary
    :return: tuple of base URL and login URL
    """
    run_mode = config["environment mode"]
    rec_type = config["record type"]
    issue_types = set(config["issue types"])
    if run_mode not in ["test", "prod"]:
        print("Invalid run mode")
        sys.exit()
    if not issue_types.issubset({"verify", "error"}):
        print("Invalid issue type")
        sys.exit()
    if rec_type not in REC_TYPES:
        print("Invalid record type")
        sys.exit()
    source_id = REC_TYPES[config["record type"]]
    manager_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                   f"/RecordManager.aspx?SourceID={source_id}")
    verifier_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                    f"/Verification/Verification.aspx?SourceID={source_id}&RecordID=")
    login_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                 f"/Login.aspx")
    return manager_url, verifier_url, login_url


def prompt_credentials() -> tuple[str, str]:
    """
    Prompt the user for their Axiom credentials
    :return: tuple of username and password
    """
    username = input("Enter your Axiom username: ").strip()
    password = pwinput.pwinput(prompt="Enter your Axiom password: ",
                               mask='*').strip()
    return username, password
