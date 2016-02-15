"""
Web panel for srcds, using gunrskite.
"""
import logging
import time
from threading import Lock
import flask_sqlalchemy
from flask import g, render_template
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

logging.getLogger("sqlalchemy").setLevel(app.config.get("SQLALCHEMY_LOG_LEVEL", logging.CRITICAL))

logger.info("Gunrskite server loading...")

# --> Bind SQLAlchemy
db.db.init_app(app)
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

# --> Register logger debug filter
app.jinja_env.filters["log_debug"] = logger.debug

# --> Add a small selection of builtins.
app.jinja_env.globals["int"] = int
app.jinja_env.globals["str"] = str
app.jinja_env.globals["float"] = float
app.jinja_env.globals["enumerate"] = enumerate
app.jinja_env.globals["round"] = round


# --> Register error handlers
@app.errorhandler(404)
def e404(e):
    return render_template("errors/404.html"), 404


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


if __name__ == "__main__":
    app.run("0.0.0.0")
