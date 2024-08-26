import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self):
        uri = os.environ.get("DATABASE_URI", "root:password@localhost/simulator")
        self.engine = create_engine(f"mysql+mysqlconnector://{uri}")
        self.Session = sessionmaker(bind=self.engine)

    def connect(self) -> None:
        print("Successfully connected to MySQL database")

    def disconnect(self) -> None:
        self.engine.dispose()
        print("MySQL connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
