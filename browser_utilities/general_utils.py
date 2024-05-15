import pwinput
import sys
import os


def generate_urls(config: dict) -> tuple[str, str, str]:
    """
    Generate the base URL and login URL
    :param config: configuration dictionary
    :return: tuple of base URL and login URL
    """
    run_mode = config["environment mode"]
    issue_types = set(config["issue types"])

    # validate the configuration
    if run_mode not in ["test", "prod"]:
        print("Invalid run mode")
        sys.exit()
    if not issue_types.issubset({"verify", "error"}):
        print("Invalid issue type")
        sys.exit()
    # add more here as needed

    # generate the URLs used by the fetcher and worker
    source_id = config["source id"]
    manager_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                   f"/RecordManager.aspx?SourceID={source_id}")
    verifier_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                    f"/Verification/Verification.aspx?SourceID={source_id}&RecordID=")
    login_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                 f"/Login.aspx")
    return manager_url, verifier_url, login_url


def prompt_credentials(env="PROD") -> tuple[str, str]:
    """
    Prompt the user for their Axiom credentials
    :return: tuple of username and password
    """
    username = os.environ.get(f"AXIOM_{env}_USERNAME")
    password = os.environ.get(f"AXIOM_{env}_PASSWORD")
    if not username or not password:
        username = input("Enter your Axiom username: ").strip()
        password = pwinput.pwinput(prompt="Enter your Axiom password: ",
                                   mask='*').strip()
    return username, password
