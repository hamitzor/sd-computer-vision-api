from mongo import db
from datetime import datetime
from sys import stderr
from config_loader import config

codes = config["codes"]


ERROR_TYPE = codes["log_type"]["ERROR"]
INFO_TYPE = codes["log_type"]["INFO"]


def _now():
    return datetime.now().replace(microsecond=0)


def _log(message, type):
    db["cv_logs"].insert_one({"date": _now(), "type": type, "message": message})


def log_error(message):
    _log(message, ERROR_TYPE)


def log_info(message):
    _log(message, INFO_TYPE)


def _console_log(message, type):
    if type == ERROR_TYPE:
        print("\033[91m"+str(_now())+" -- "+ERROR_TYPE+" -- "+message, file=stderr)
    else:
        print(str(_now())+" -- "+INFO_TYPE+" -- "+message)


def console_log_error(message):
    _console_log(message, ERROR_TYPE)


def console_log_info(message):
    _console_log(message, INFO_TYPE)
