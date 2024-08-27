from base64 import b64encode
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PostgresDatabase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        connection_key = cls._generate_connection_key(**kwargs)

        if connection_key not in cls._instances:
            cls._instances[connection_key] = super(__class__, cls).__new__(cls)

            if kwargs == {}:
                user = getenv("METAMORFO_POSTGRES_USER")
                pssw = getenv("METAMORFO_POSTGRES_PASSWORD")
                host = getenv("METAMORFO_POSTGRES_HOST")
                port = getenv("METAMORFO_POSTGRES_PORT")
                database = getenv("METAMORFO_POSTGRES_DB")
            else:
                user = kwargs["username"]
                pssw = kwargs["password"]
                host = kwargs["host"]
                port = kwargs["port"]
                database = kwargs["database"]
            con_ = (
                f"postgresql+psycopg2://{user}:{pssw}@{host}:{port}/{database}"
            )
            cls._instances[connection_key].engine = create_engine(con_)
        return cls._instances[connection_key]

    @staticmethod
    def _generate_connection_key(**kwargs):
        keys_bytes = str(kwargs).encode("utf-8")
        return b64encode(keys_bytes).decode("utf-8")

    def execute_query(self, query, params=None):
        with self.engine.connect() as conn:
            if params is None:
                result = conn.execute(query)
            else:
                result = conn.execute(query, params)

            return result
