from sqlalchemy import create_engine, Column, Integer, String, Table, DateTime, exists, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import scoped_session
from . import jsonalchemy

Base = declarative_base()


# Function for creating the engine and session.
def create_sess(uri):
    engine = create_engine(uri)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return engine, Session


class Event(Base):
    """Describes an event."""
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)

    event_data = Column(jsonalchemy.JSONAlchemy(String(32768)))  # Stupid row size limits in mysql.

    user_id = Column(Integer, ForeignKey("user.id"))
    server_id = Column(Integer, ForeignKey("server.id"))


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    steamid = Column(String(255), unique=True)
    events = relationship(Event, uselist=True, backref='user')

    kills = Column(Integer)
    deaths = Column(Integer)

    last_seen_name = Column(String(255))

    points = Column(Integer)


class Server(Base):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True)

    ip = Column(String(255), unique=True)
    port = Column(Integer)
