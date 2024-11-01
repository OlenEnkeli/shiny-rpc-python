import asyncio
import logging

from shiny_rpc.server import Server
from shiny_rpc.utils import setup_rich_logging

from .methods import handler

server = Server(
    host='127.0.0.1',
    port=7777,
    log_level=logging.DEBUG,
    log_messages=True,
    message_handler=handler,
)


if __name__ == '__main__':
    setup_rich_logging()
    asyncio.run(server.run())
