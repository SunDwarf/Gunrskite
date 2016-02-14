"""
Srcds utilities.
"""
import requests
from flask import abort

from wser_app import app
from flask_cache import Cache

cache = app.fl_cache
assert isinstance(app.fl_cache, Cache)

from valve.source import a2s
import logging

logger = logging.getLogger("Gunrskite::Webpanel")

steamid64ident = 76561197960265728


def get_server_info(ip, port):
    # Ping the server.
    querier = a2s.ServerQuerier((ip, port))
    try:
        return dict(querier.get_info())
    except a2s.NoResponseError:
        return {"server_name": "Unknown", "player_count": 0, "max_players": 0}


# Technically not srcds, but it's steam API.
@cache.memoize(timeout=120 * 60)  # 2 hours
def get_steam_info(steamid3):
    commid = usteamid_to_commid(steamid3)

    r = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
                     params={"key": app.config["STEAM_API_KEY"],
                             "format": "json",
                             "steamids": commid})
    print(r.url)
    if r.status_code == 403:
        raise Exception("Steam API returned 403 - Is your API key correct?")

    js = r.json()["response"]["players"]
    print(js)
    if len(js):
        return js[0]
    else:
        raise Exception("Steam API returned 404 - Is your steamid correct?")


def get_steam_avatar(steamid3: str, size="full"):
    data = get_steam_info(steamid3)

    return data["avatar{}".format(size)]


# https://gist.github.com/bcahue/4eae86ae1d10364bb66d
def usteamid_to_steamid(usteamid):
    for ch in ['[', ']']:
        if ch in usteamid:
            usteamid = usteamid.replace(ch, '')

    usteamid_split = usteamid.split(':')
    steamid = ['STEAM_0:']

    z = int(usteamid_split[2])

    if z % 2 == 0:
        steamid.append('0:')
    else:
        steamid.append('1:')

    steamacct = z // 2

    steamid.append(str(steamacct))

    return ''.join(steamid)


def usteamid_to_commid(usteamid):
    for ch in ['[', ']']:
        if ch in usteamid:
            usteamid = usteamid.replace(ch, '')

    usteamid_split = usteamid.split(':')
    commid = int(usteamid_split[2]) + steamid64ident

    return commid
