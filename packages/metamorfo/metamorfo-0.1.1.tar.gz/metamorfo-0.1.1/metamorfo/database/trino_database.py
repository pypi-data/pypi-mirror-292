from base64 import b64encode
from os import getenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TrinoDatabase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        connection_key = cls._generate_connection_key(**kwargs)

        if connection_key not in cls._instances:
            cls._instances[connection_key] = super(__class__, cls).__new__(cls)

            if kwargs == {}:
                user = getenv("TRINO_USER")
                pssw = getenv("TRINO_PASSWORD")
                host = getenv("TRINO_HOST")
                port = getenv("TRINO_PORT")
                source = getenv("TRINO_SOURCE")
            else:
                user = kwargs["username"]
                pssw = kwargs["password"]
                host = kwargs["host"]
                port = kwargs["port"]
                source = kwargs["source"] if 'source' in kwargs is not None else 'default'

            if pssw is not None:
                con_ = f"trino://{user}:{pssw}@{host}:{port}?source={source}"
            else:
                con_ = f"trino://{user}@{host}:{port}?source={source}"
            cls._instances[connection_key].engine = create_engine(con_)
            cls.ck = connection_key
        return cls._instances[connection_key]

    @staticmethod
    def _generate_connection_key(**kwargs):
        keys_bytes = str(kwargs).encode("utf-8")
        return b64encode(keys_bytes).decode("utf-8")

    def execute_query(self, query, params=None):
        with self._instances[self.ck].engine.connect() as conn:
            if params is None:
                result = conn.execute(text(query))
            else:
                result = conn.execute(text(query), params)

            return result
