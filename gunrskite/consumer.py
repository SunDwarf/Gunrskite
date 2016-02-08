"""
Event data consumer.

This puts everything into the DB appropriately.
"""
import logging
from gunrskite import db


attrdict = type("AttrDict", (dict,), {"__getattr__": dict.__getitem__, "__setattr__": dict.__setitem__})

logger = logging.getLogger("Gunrskite::Consumer")


def consume(cfg, d: attrdict, server: db.Server, session):
    """
    Consume data from the attrdict, and load it into the DB.
    """
    logger.debug("Consuming data into database...")
    # Attempt to load user.
    user = session.query(db.User).filter(db.User.steamid == d.steamid).first()
    if not user:
        # Create a user.
        user = db.User(steamid=d.steamid, last_seen_name=d.displayname)
        session.add(user)
    suser = session \
        .query(db.ServerUser) \
        .join(db.ServerUser.user).join(db.ServerUser.server) \
        .filter(db.ServerUser.user == user, db.ServerUser.server == server).first()
    if not suser:
        suser = db.ServerUser(points=cfg["INITIAL_POINTS"], kills=0, deaths=0)
        suser.user = user
        suser.server = server
        session.add(suser)
    # More switches for actions.
    if d.action == "say":
        event_data = {"action": "say", "msg": d.msg}
        event = db.Event(event_data=event_data)
    elif d.get("killed", False):
        if d.suicide:
            weapon = d.method
            target = None
        else:
            weapon = d.killer_weapon
            target = d.target
        event_data = {"action": "killed", "suicide": d.suicide, "weapon": weapon,
                      "target": target}
        # Update points
        if not d.suicide:
            ukilled = session.query(db.User).filter(db.User.steamid == d.target.steamid).first()
            if not ukilled:
                ukilled = db.User(steamid=d.target.steamid, last_seen_name=d.target.displayname)
                session.add(ukilled)
            killed = session.query(db.ServerUser) \
                .join(db.ServerUser.user).join(db.ServerUser.server) \
                .filter(db.ServerUser.user == ukilled, db.ServerUser.server == server).first()
            if killed:
                killed.points -= cfg["POINTS_LOST_ON_DEATH"]
                killed.deaths = (killed.deaths + 1) if killed.deaths else 1
                session.add(killed)
            else:
                killed = db.ServerUser(points=cfg["INITIAL_POINTS"], kills=0, deaths=0)
                killed.user = ukilled
                killed.server = server
                session.add(killed)
            suser.points += cfg["POINTS_ON_KILL"]
            suser.kills = (suser.kills + 1) if suser.kills else 1
        else:
            suser.points -= cfg["POINTS_LOST_ON_DEATH"]
            suser.deaths = (suser.deaths + 1) if suser.deaths else 1
        session.add(suser)
        event = db.Event(event_data=event_data)
    else:
        return  # TODO: More events
    event.user = user
    event.server = server
    event.date = d.date
    session.add(event)
    session.commit()
    session.close()
