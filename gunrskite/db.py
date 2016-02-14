import logging
import os
from flask.ext.security import RoleMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Table, DateTime, exists, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm import scoped_session
from . import jsonalchemy
from flask import Config

cfg = Config(os.path.abspath("."))
cfg.from_pyfile("config.py")

db = SQLAlchemy()

logger = logging.getLogger("Gunrskite::Database")

# Check if we're inside the UDP listener, or not.
if os.environ.get("INSIDE_LISTENER", "n") == "y":
    print("Using declarative_base() for model base.")
    Base = declarative_base()
else:
    # Switch to using Flask-SQLAlchemy's model.
    print("Using db.Model for model base.")
    Base = db.Model
engine = create_engine(cfg["SQLALCHEMY_DATABASE_URI"], pool_recycle=3600)


# Function for creating the engine and session.
def create_sess():
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session


class Event(Base):
    """Describes an event."""
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)

    event_data = Column(jsonalchemy.JSONAlchemy(String(32768)))  # Stupid row size limits in mysql.

    user_id = Column(Integer, ForeignKey("user.id"))
    server_id = Column(Integer, ForeignKey("server.id"))
    server = relationship("Server", uselist=False)

    action = Column(String(255))

    date = Column(DateTime())


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    steamid = Column(String(255), unique=True)
    events = relationship(Event, uselist=True, backref='user')

    last_seen_name = Column(String(255))

    points = Column(Integer)


class Server(Base):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True)

    ip = Column(String(255), unique=True)
    port = Column(Integer)


class ServerUser(Base):
    __tablename__ = "server_user"
    id = Column(Integer, primary_key=True)

    points = Column(Integer, default=cfg["INITIAL_POINTS"])

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)

    server_id = Column(Integer, ForeignKey(Server.id))
    server = relationship(Server)

    kills = Column(Integer, default=0, nullable=False)
    deaths = Column(Integer, default=0, nullable=False)


# Define panel models
roles_users = Table('roles_users', Base.metadata,
                    Column('user_id', Integer(), ForeignKey('panel_user.id')),
                    Column('role_id', Integer(), ForeignKey('role.id')))


class PanelUser(Base):
    __tablename__ = "panel_user"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))


class Role(Base, RoleMixin):
    __tablename__ = "role"
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
