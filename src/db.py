from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse
import datetime


class DB:
    def __init__(self, user, password, host):
        username = urllib.parse.quote_plus(user)
        password = urllib.parse.quote_plus(password)
        client = MongoClient("mongodb://%s:%s@%s" % (username, password, host), authSource='sd')
        self._db = client["sd"]

    def get_video(self, id):
        return self._db["videos"].find_one({'_id': ObjectId(id)})

    def update_video(self, id, new_values):
        return self._db["videos"].update_one({'_id': ObjectId(id)}, {"$set": new_values})

    def delete_detected_objects(self, video_id):
        return self._db["detected_objects"].delete_many({'video_id': video_id})

    def insert_detected_objects(self, detected_object_list):
        return self._db["detected_objects"].insert_many(detected_object_list)

    def insert_log(self, type, message):
        return self._db["logs"].insert_one({"date": datetime.datetime.now(), "type": type, "message": message})
