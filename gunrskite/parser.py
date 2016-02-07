"""
Parse srcds log messages.
"""
import dateutil.parser
import logging
import re
from gunrskite import db

logger = logging.getLogger("Gunrskite::Parse")

get_inside_quotes = re.compile(r'\"(.+?)\"')
username_regex = re.compile(r"([^<]*)<([0-9]*)><(\[U:[0-9]:[0-9]{0,9}])><([A-Z]?[a-z]{0,})?>")
ingame_actions = re.compile(r"(say|killed|committed suicide with|joined team|changed role to|triggered)")
misc_actions = re.compile(r"(connected|entered the game|disconnected)")

attrdict = type("AttrDict", (dict,), {"__getattr__": dict.__getitem__, "__setattr__": dict.__setitem__})


def parse_user(action, d: attrdict, data: str):
    # Parse username data.
    username_data_raw = get_inside_quotes.findall(data)[0]
    logger.debug("Raw username data: {}".format(username_data_raw))
    d._username_data = username_regex.findall(username_data_raw)[0]
    logger.debug("Display Name: {} / Player ID: {} / SteamID: {} / Team: {}".format(*d._username_data))
    d.displayname, d.playerid, d.steamid, d.team = d._username_data

    # Parse action data
    d.action = action
    if d.action == "say":
        d.msg = get_inside_quotes.findall(data)[1]
        logger.info("Player {} ({}) said: {}".format(d.steamid, d.displayname, d.msg))
    elif d.action == "killed":
        d.killed = True
        d.suicide = False
        target = get_inside_quotes.findall(data)[1]
        logger.debug("Target: {}".format(target))
        d.target = attrdict()
        target_ud = username_regex.findall(target)[0]
        d.target.displayname, d.target.playerid, d.target.steamid, d.target.team = target_ud
        d.killer_weapon = get_inside_quotes.findall(data)[2]
        logger.info("Player {} ({}) killed {} ({}) with {}"
                    .format(d.steamid, d.displayname, d.target.steamid, d.target.displayname, d.killer_weapon))
    elif d.action == "committed suicide with":
        d.killed = True
        d.suicide = True
        d.method = get_inside_quotes.findall(data)[1]
        logger.debug("Player {} ({}) killed self with {}".format(d.steamid, d.displayname, d.method))
    elif d.action == "joined team":
        d.new_team = get_inside_quotes.findall(data)[1]
        logger.info("Player {} ({}) switched team to {}".format(d.steamid, d.displayname, d.new_team))
    elif d.action == "changed role to":
        d.new_role = get_inside_quotes.findall(data)[1]
        logger.info("Player {} ({}) changed class to {}".format(d.steamid, d.displayname, d.new_role))


def parse_misc(action, d: attrdict, data: str):
    username_data_raw = get_inside_quotes.findall(data)[0]
    logger.debug("Raw username data: {}".format(username_data_raw))
    d._username_data = username_regex.findall(username_data_raw)[0]
    logger.debug("Display Name: {} / Player ID: {} / SteamID: {}".format(*d._username_data))
    d.displayname, d.playerid, d.steamid, d.team = d._username_data

    d.action = action

    if d.action == "connected":
        d.addr = get_inside_quotes.findall(data)[1]
        logger.info("User {} connected from {}".format(d.steamid, d.addr))
    elif d.action == "entered the game":
        logger.info("User {} ({}) spawned".format(d.steamid, d.displayname))
    elif d.action == "disconnected":
        d.disconnected = True
        d.reason = get_inside_quotes.findall(data)[1]
        logger.info("User {} ({}) disconnected (reason: {})".format(d.steamid, d.displayname, d.reason))


def parse(data, server: db.Server):
    d = attrdict()

    logger.debug("Attempting data parse.")

    # Chop off the first 7 bytes
    chopped = data[7:]
    # Chop off last bytes
    chopped = chopped[:-2]
    chopped = chopped.decode(encoding='utf-8')
    # Extract the date.
    date_str = ':'.join(chopped.split(':')[0:3])
    # Parse it using dateutil.
    d.date = dateutil.parser.parse(date_str)
    d.server = server
    logger.debug("Date is {}".format(d.date))

    # Horrible nested if
    iaf = ingame_actions.findall(chopped)
    if iaf:
        parse_user(iaf[0], d, chopped)
    else:
        maf = misc_actions.findall(chopped)
        if maf:
            parse_misc(maf[0], d, chopped)
        else:
            logger.info("Message did not meet any server information, skipping.")

    return d
