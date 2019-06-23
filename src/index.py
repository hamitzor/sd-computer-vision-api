import json
from server import start_server
from config_loader import config

start_server(config["cv_api"]["host"], config["cv_api"]["port"])
