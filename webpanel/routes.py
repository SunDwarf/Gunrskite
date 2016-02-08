"""
Routes for the app.
"""
from flask import Blueprint, render_template
from gunrskite import db
from webpanel import srcds

routes_bp = Blueprint("gunrskite", __name__)


@routes_bp.route("/")
def index():
    servers_s = db.db.session.query(db.Server).all()
    servers = [srcds.get_server_info(serv.ip, serv.port) for serv in servers_s]
    return render_template("index.html", servers=servers)
