"""
Srcds utilities.
"""
from wser_app import app
from flask_cache import Cache

cache = app.fl_cache
assert isinstance(cache, Cache)

from valve.source import a2s


@cache.memoize(timeout=600)
def get_server_info(ip, port):
    # Ping the server.
    querier = a2s.ServerQuerier((ip, port))
    return dict(querier.get_info())
