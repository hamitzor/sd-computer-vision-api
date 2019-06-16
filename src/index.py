"""
python3 src/index.py --mongodb-user sdadmin --mongodb-password root --mongodb-host localhost --mongodb-name sd --port 8001 --host localhost
"""

import json
import argparse
from db import db
from server import start_server

argparse = argparse.ArgumentParser()
argparse.add_argument("-dbh", "--mongodb-host", required=True, help="MongoDB host")
argparse.add_argument("-dbu", "--mongodb-user", required=True, help="MongoDB username")
argparse.add_argument("-dbp", "--mongodb-password", required=True, help="MongoDB password")
argparse.add_argument("-dbn", "--mongodb-name", required=True, help="MongoDB database name")
argparse.add_argument("-l", "--host", default="localhost", help="Server hostname")
argparse.add_argument("-p", "--port", default=8000, help="Server port", type=int)


args = argparse.parse_args()

db.connect(args.mongodb_host, args.mongodb_user, args.mongodb_password, args.mongodb_name)


start_server(args.host, args.port)
