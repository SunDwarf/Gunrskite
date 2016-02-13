"""
Rendering utilities.
"""
from sqlalchemy import desc

from gunrskite import db


def get_top_player(server: db.Server):
    player = db.db.session.query(db.ServerUser) \
        .join(db.ServerUser.server) \
        .filter(db.ServerUser.server == server) \
        .order_by(desc(db.ServerUser.points)) \
        .limit(1) \
        .first()

    return player
