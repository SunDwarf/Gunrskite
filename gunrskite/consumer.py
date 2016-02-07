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
        user = db.User(steamid=d.steamid, last_seen_name=d.displayname, points=cfg["INITIAL_POINTS"])
        session.add(user)

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
            killed = session.query(db.User).filter(db.User.steamid == d.target.steamid).first()
            if killed:
                killed.points -= cfg["POINTS_LOST_ON_DEATH"]
                killed.deaths += 1
                session.add(killed)
            user.points += cfg["POINTS_ON_KILL"]
            user.kills += 1
        else:
            user.points -= cfg["POINTS_LOST_ON_DEATH"]
            user.deaths += 1
        session.add(user)
        event = db.Event(event_data=event_data)
    else:
        return  # TODO: More events
    event.user = user
    event.server = server
    event.date = d.date
    session.add(event)
    session.commit()
