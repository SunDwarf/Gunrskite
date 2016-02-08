"""
Web panel for srcds, using gunrskite.
"""
import logging
import time
from threading import Lock

import flask_sqlalchemy
from flask import g
from flask.ext.cache import Cache
from flask.ext.security import SQLAlchemyUserDatastore

from gunrskite import db

# --> App init
from wser_app import app

# --> Load config
app.config.from_pyfile("config.py")

# --> Set up logging

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(name)s -> %(message)s')
root = logging.getLogger()

root.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
root.addHandler(consoleHandler)

logger = logging.getLogger("Gunrskite::Webpanel")

logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)

logger.info("Gunrskite server loading...")


# --> Bind SQLAlchemy

class FakeSQLAlchemy(flask_sqlalchemy.SQLAlchemy):
    """
    A FakeSQLAlchemy class wraps the manual database handling in a bit of mapping, and lets Flask-SQLAlchemy take
    over if needed.
    """

    def __init__(self, app=None, use_native_unicode=True, session_options=None, metadata=None):
        if session_options is None:
            session_options = {}

        session_options.setdefault('scopefunc', flask_sqlalchemy.connection_stack.__ident_func__)
        self.use_native_unicode = use_native_unicode
        self.session = db.create_sess()
        self.Model = db.Base
        self.Query = flask_sqlalchemy.BaseQuery
        self._engine_lock = Lock()
        self.app = app
        flask_sqlalchemy._include_sqlalchemy(self)

        if app is not None:
            self.init_app(app)


sqlalchemy = FakeSQLAlchemy(app)
db.db = sqlalchemy

logger.info("SQLAlchemy binding created with engine {}".format(db.engine))

# --> Flask-Security
user_datastore = SQLAlchemyUserDatastore(db.db, db.User, db.Role)

# --> Flask-Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# Blerg
app.fl_cache = cache

# --> Flask-DebugToolbar
from flask_debugtoolbar import DebugToolbarExtension

toolbar = DebugToolbarExtension(app)

# --> Register blueprints
from webpanel import routes

app.register_blueprint(routes.routes_bp)


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

if __name__ == "__main__":
    app.run("0.0.0.0")
