"""
Gunrskite UDP Logging Server

Binds to 0.0.0.0:23887 by default.
"""
import asyncio
import logging
import argparse
from gunrskite import parser as gparse

loop = asyncio.get_event_loop()

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(name)s -> %(message)s')
root = logging.getLogger()

root.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
root.addHandler(consoleHandler)

logger = logging.getLogger("Gunrskite-udp")

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bind", help="IP address to bind to", default="0.0.0.0")
parser.add_argument("-p", "--port", help="Port to bind to", default=23887, type=int)
args = parser.parse_args()


class LoggerProtocol(object):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logger.info("Recieved message {}".format(data))
        msgdata = gparse.parse(data)
        print(msgdata)


def __main__():
    logger.info("Gunrskite logging server loading")
    logger.info("Binding on UDP to {}:{}".format(args.bind, args.port))
    listen_server = loop.create_datagram_endpoint(
        LoggerProtocol, local_addr=(args.bind, args.port))
    transport, protocol = loop.run_until_complete(listen_server)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()

if __name__ == "__main__":
    __main__()
