"""
Routes for the app.
"""
from flask import Blueprint, render_template

routes_bp = Blueprint("gunrskite", __name__)


@routes_bp.route("/")
def index():
    return render_template("index.html")
