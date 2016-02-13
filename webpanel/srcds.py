"""
Srcds utilities.
"""
from wser_app import app
from flask_cache import Cache

cache = app.fl_cache
assert isinstance(cache, Cache)

from valve.source import a2s

steamid64ident = 76561197960265728


@cache.memoize(timeout=600)
def get_server_info(ip, port):
    # Ping the server.
    querier = a2s.ServerQuerier((ip, port))
    return dict(querier.get_info())


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
