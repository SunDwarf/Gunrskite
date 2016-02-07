"""
Parse srcds log messages.
"""
import dateutil.parser
import logging
import re

logger = logging.getLogger("Gunrskite-udp")

get_inside_quotes = re.compile(r'\"(.+?)\"')
username_regex = re.compile(r"([^<]*)(<[0-9]*>)(<\[U:[0-9]:[0-9]{0,9}]>)(<[A-Z][a-z]{2,}>)")
actions = re.compile(r"(say|killed|committed suicide with|joined team|changed role to)")

attrdict = type("AttrDict", (dict,), {"__getattr__": dict.__getitem__, "__setattr__": dict.__setitem__})


def parse_user(d: attrdict, data: str):
    # Parse username data.
    username_data_raw = get_inside_quotes.findall(data)[0]
    logger.debug("Raw username data: {}".format(username_data_raw))
    d._username_data = username_regex.findall(username_data_raw)[0]
    logger.debug("Display Name: {} / Player ID: {} / SteamID: {} / Team: {}".format(*d._username_data))
    d.displayname, d.playerid, d.steamid, d.team = d._username_data

    d.action = actions.findall(data)[0]
    if d.action == "say":
        d.msg = get_inside_quotes.findall(data)[1]
        logger.info("Player {} said: {}".format(d.steamid, d.msg))
    elif d.action == "killed":
        target = get_inside_quotes.findall(data)[1]
        logger.debug("Target: {}".format(target))
        d.target = attrdict()
        target_ud = username_regex.findall(target)[0]
        d.target.displayname, d.target.playerid, d.target.steamid, d.target.team = target_ud
        d.killer_weapon = get_inside_quotes.findall(data)[2]
        logger.info("Player {} ({}) killed {} ({}) with {}"
                    .format(d.steamid, d.displayname, d.target.steamid, d.target.displayname, d.killer_weapon))

def parse(data):
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
    logger.debug("Date is {}".format(d.date))

    if actions.findall(chopped):
        parse_user(d, chopped)
    else:
        logger.info("Message did not meet any server information, skipping.")

    return d
