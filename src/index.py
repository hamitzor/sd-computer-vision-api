import json
from db import db
from server import start_server
from config_loader import config


db.connect(config["mongo"]["host"], config["mongo"]["user"], config["mongo"]["password"], config["mongo"]["name"])

start_server(config["cv_api"]["host"], config["cv_api"]["port"])
