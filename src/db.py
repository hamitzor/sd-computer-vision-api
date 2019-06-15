from pymongo import MongoClient
from urllib.parse import quote_plus


class DB:
    def __init__(self):
        self._connected = False

    def connect(self, host, user, password, name):
        if self._connected:
            raise ConnectionError("already connected")

        user = quote_plus(user)
        password = quote_plus(password)

        client = MongoClient("mongodb://%s:%s@%s" % (user, password, host), authSource=name)
        self._db = client[name]
        self._connected = True

    def find_one(self, col, query={}, fields=None):
        return self._db[col].find_one(query, fields)

    def find(self, col, query={}, fields=None):
        return self._db[col].find(query, fields)

    def insert_one(self, col, val):
        res = self._db[col].insert_one(val)
        return res.inserted_id

    def insert_many(self, col, vals):
        res = self._db[col].insert_many(vals)
        return res.inserted_ids

    def delete_one(self, col, query={}):
        res = self._db[col].delete_one(query)
        return res.deleted_count

    def delete_many(self, col, query={}):
        res = self._db[col].delete_many(query)
        return res.deleted_count

    def update_one(self, col, update, query={}):
        res = self._db[col].update_one(query, update)
        return res.modified_count

    def update_many(self, col, update, query={}):
        res = self._db[col].update_many(query, update)
        return res.modified_count


db = DB()
