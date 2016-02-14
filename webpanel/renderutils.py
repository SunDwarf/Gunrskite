"""
Rendering utilities.
"""
from sqlalchemy import desc
from sqlalchemy.sql import func
from gunrskite import db
from webpanel import srcds


def get_top_player(server: db.Server):
    """Gets the top player from the server."""
    player = db.db.session.query(db.ServerUser) \
        .join(db.ServerUser.server) \
        .filter(db.ServerUser.server == server) \
        .order_by(desc(db.ServerUser.points)) \
        .limit(1) \
        .first()

    return player


def get_steam_avatar(steamid3: str, clss: str):
    """Gets the steam avatar for a user, returning the HTML"""
    return '<img src="{}" class="{}" />'.format(srcds.get_steam_avatar(steamid3), clss)


def get_all_points(server: db.Server):
    """
    Gets all points for a specific server.
    """
    points = db.db.session.query(func.sum(db.ServerUser.points)) \
        .join(db.ServerUser.server) \
        .filter(db.ServerUser.server == server) \
        .limit(1) \
        .scalar()

    return points
