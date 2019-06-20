from db import db
from datetime import datetime
from sys import stderr


def _now():
    return datetime.now().replace(microsecond=0)


def _log(message, type):
    db.insert_one("cv_logs", {"date": _now(), "type": type, "message": message})


def log_error(message):
    _log(message, "ERROR")


def log_info(message):
    _log(message, "INFO")


def _console_log(message, type):
    if type == "ERROR":
        print("\033[91m"+str(_now())+" -- ERROR -- "+message, file=stderr)
    else:
        print(str(_now())+" -- INFO -- "+message)


def console_log_error(message):
    _console_log(message, "ERROR")


def console_log_info(message):
    _console_log(message, "INFO")
