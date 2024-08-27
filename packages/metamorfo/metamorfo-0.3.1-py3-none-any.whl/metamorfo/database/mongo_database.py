from base64 import b64encode
from os import getenv

from pymongo import MongoClient


class MongoDatabase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        connection_key = cls._generate_connection_key(**kwargs)

        if connection_key not in cls._instances:
            cls._instances[connection_key] = super(__class__, cls).__new__(cls)

            if kwargs == {}:
                user = getenv("METAMORFO_MONGO_USER")
                pssw = getenv("METAMORFO_MONGO_PASSWORD")
                host = getenv("METAMORFO_MONGO_HOST")
                port = getenv("METAMORFO_MONGO_PORT")
            else:
                user = kwargs["username"]
                pssw = kwargs["password"]
                host = kwargs["host"]
                port = kwargs["port"]
            cls._instances[connection_key].__connect(user, pssw, host, port)
        return cls._instances[connection_key]

    @staticmethod
    def _generate_connection_key(**kwargs):
        keys_bytes = str(kwargs).encode("utf-8")
        return b64encode(keys_bytes).decode("utf-8")

    def __connect(self, mongo_user, mongo_pssw, mongo_host, mongo_port):
        self._mongo_client = MongoClient(
            f"mongodb://{mongo_user}:{mongo_pssw}@{mongo_host}:{mongo_port}/admin"
        )

    def list_dbs(self):
        return self._mongo_client.list_database_names()

    def set_db(self, db):
        self.db = db

    def list_collections(self, db):
        return self._mongo_client[db].list_collection_names()

    def getcollection(self, collection):
        return self._mongo_client[self.db][collection]
