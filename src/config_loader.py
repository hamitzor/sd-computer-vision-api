import json
from urllib.request import urlopen
import argparse

argparse = argparse.ArgumentParser()
argparse.add_argument("-c", "--config-endpoint", required=True, help="Configuration endpoint")

args = argparse.parse_args()

config_endpoint = args.config_endpoint

config = (json.loads(urlopen(config_endpoint).read().decode("utf-8")))["payload"]
