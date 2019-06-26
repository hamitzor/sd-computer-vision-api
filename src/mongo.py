from pymongo import MongoClient
from urllib.parse import quote_plus
from config_loader import config


host = config["mongo"]["hostname"]
user = config["mongo"]["username"]
password = config["mongo"]["password"]
name = config["mongo"]["db_name"]


user = quote_plus(user)
password = quote_plus(password)
client = MongoClient("mongodb://%s:%s@%s" % (user, password, host), authSource=name)
db = client[name]
