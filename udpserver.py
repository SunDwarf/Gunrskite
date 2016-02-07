"""
Gunrskite UDP Logging Server

Binds to 0.0.0.0:23887 by default.
"""
import asyncio
import logging
import os

import sqlalchemy

from gunrskite import parser as gparse
from gunrskite import db as db
from gunrskite import consumer as consumer
from flask import Config

cfg = Config(os.path.abspath("."))
cfg.from_pyfile("config.py")

loop = asyncio.get_event_loop()

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(name)s -> %(message)s')
root = logging.getLogger()

root.setLevel(cfg.get("LOG_LEVEL", logging.INFO))

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
root.addHandler(consoleHandler)

logger = logging.getLogger("Gunrskite::Listener")

logging.getLogger("sqlalchemy").setLevel(cfg.get("SQLALCHEMY_LOG_LEVEL", logging.CRITICAL))

session = db.create_sess()


class LoggerProtocol(object):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logger.debug("Recieved message {} from {}".format(data, addr))
        # Get server.
        server = session.query(db.Server).filter(db.Server.ip == addr[0], db.Server.port == addr[1]).first()
        if not server:
            logger.error("Recieved message from unknown server! Address: {} / Ignoring".format(addr))
            return
        msgdata = gparse.parse(data, server)
        try:
            consumer.consume(cfg, msgdata, server, session)
        except sqlalchemy.exc.InvalidRequestError:
            logger.error("MySQL has suddenly gained dementia - rolling back transactions")
            if session.is_active:
                session.rollback()


def __main__():
    logger.info("Gunrskite logging server loading")
    logger.info("Database is connected on {}".format(cfg["SQLALCHEMY_URI"]))
    logger.info("Binding on UDP to {}:{}".format(*cfg["LISTENER_BIND"]))
    listen_server = loop.create_datagram_endpoint(
        LoggerProtocol, local_addr=cfg["LISTENER_BIND"])
    transport, protocol = loop.run_until_complete(listen_server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


if __name__ == "__main__":
    __main__()
