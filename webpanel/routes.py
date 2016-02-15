"""
Routes for the app.
"""
from flask import Blueprint, render_template, request
from gunrskite import db
from webpanel import srcds, renderutils

routes_bp = Blueprint("gunrskite", __name__)


@routes_bp.route("/server/<int:server_id>")
def server_info(server_id):
    # Get the server
    server = db.Server.query.filter(db.Server.id == server_id).first_or_404()
    # Get the page args.
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except:
        page = 1
    return render_template("serverinfo.html", server=server, srcds=srcds, renderutils=renderutils,
                           current_page=1)


@routes_bp.route("/")
def index():
    servers_s = db.db.session.query(db.Server).all()
    servers = [(srcds.get_server_info(serv.ip, serv.port), serv) for serv in servers_s]
    return render_template("index.html", servers=servers, renderutils=renderutils)
