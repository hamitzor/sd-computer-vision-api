from pymongo import MongoClient
from urllib.parse import quote_plus
from config_loader import config


host = config["mongo"]["host"]
user = config["mongo"]["user"]
password = config["mongo"]["password"]
name = config["mongo"]["name"]


user = quote_plus(user)
password = quote_plus(password)
client = MongoClient("mongodb://%s:%s@%s" % (user, password, host), authSource=name)
db = client[name]
