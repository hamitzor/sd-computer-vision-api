import json
import argparse

argparse = argparse.ArgumentParser()
argparse.add_argument("-c", "--config", required=True, help="Configuration file path")

args = argparse.parse_args()


with open(args.config, "r") as f:
    config = json.load(f)
