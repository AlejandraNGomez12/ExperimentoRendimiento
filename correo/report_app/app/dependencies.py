import os
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine

class Database:
    _engine: Engine = None

    @staticmethod
    def get_engine() -> Engine:
        if not Database._engine:
            Database._engine = create_engine(
                f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
            )
        return Database._engine


def create_db_and_tables():
    SQLModel.metadata.create_all(Database.get_engine())


def get_session():
    with Session(Database.get_engine()) as session:
        yield session
