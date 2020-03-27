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


class AuthKeys(Base):
    __tablename__ = 'auth'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, server_default=func.now())
    used_on = Column(DateTime)
    created_by = Column(Integer)
    used_by = Column(Integer)
    code = Column(String(10))

class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    created_on = Column(DateTime, server_default=func.now())
    message_type = Column(String(20))
    language = Column(String(50))
    sent_by = Column(Integer)


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    created_on = Column(DateTime, server_default=func.now())
    role = Column(String(20))
    language = Column(String(50))

if __name__ == "__main__":
    engine= db_connect()
    create_table(engine)