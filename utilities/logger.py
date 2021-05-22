from pathlib import Path
from datetime import date, datetime

utilities_dir = Path(__file__).parent
base_dir = utilities_dir.parent
resource_dir = Path(str(base_dir) + "/resource")

log_tags = {"INFO": "INFO", "DEBUG": "DEBUG",
            "WARNING": "WARNING", "ERROR": "ERROR", "CRITICAL": "CRITICAL", "ALERT": "ALERT"}

# change silent_logging to True,if you just want to log to file
silent_logging = False


def add_log(log: str, log_tag: str = "INFO"):
    """
    The function to add string to log file and console with tag.

    Parameters:
        log (str): The string that saved to log file.
        log_tag (str): The string that used as tag in log file.
    """
    today = date.today()
    now = datetime.now()
    log_tag = log_tags.get(log_tag, "INFO")
    log = f"{now}:{log_tag}|{log}\n"
    if log.endswith("\n\n"):
        log = log.replace("\n\n", "\n")
    log_path = Path(str(resource_dir) + f"/logs/logfile--{today}.log")
    with open(log_path, "a") as log_file:
        log_file.write(log)
    if not silent_logging:
        print(log)
