import json
from config_loader import config

codes_path = config["codes"]["path"]

with open(codes_path, "r") as f:
    codes = json.load(f)
