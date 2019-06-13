from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse
from argument_loader import args

username = urllib.parse.quote_plus(args.mongodb_user)
password = urllib.parse.quote_plus(args.mongodb_password)
host = args.mongodb_host

client = MongoClient("mongodb://%s:%s@%s" % (username, password, host), authSource='sd',)
db = client["sd"]


def get_video_path(id):
    return (db["videos"].find_one({'_id': ObjectId(id)}))["path"]


def insert_object(object_info):
    return
