from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)

Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine("sqlite:///data/covid.db")


def create_table(engine):
    Base.metadata.create_all(engine)


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(100))
    telegram_id = Column(String(100))
    created_on = Column(DateTime, server_default=func.now())
    session_id = Column(String(200))
    role = Column(String(20))
    language = Column(String(50))

if __name__ == "__main__":
    engine= db_connect()
    create_table(engine)