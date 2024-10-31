import asyncio
import logging
from asyncio import LimitOverrunError, open_connection
from logging import getLogger
from socket import socket
from uuid import uuid4

from shiny_rpc.constants import MESSAGE_SEPARATOR
from shiny_rpc.errors import ClientFatalError
from shiny_rpc.messages import Request, Response


class BaseClient:
    host: str
    port: int
    server: socket
    max_message_size: int
    timeout_ms: int

    is_connected: bool
    locking_event: asyncio.Event

    writer: asyncio.StreamWriter
    reader: asyncio.StreamReader
    logger: logging.Logger

    def __init__(
        self,
        host: str,
        port: int,
        max_message_size: int = 2**20,  # 1 MB
        timeout_ms: int = 5000,  # 5 second
    ) -> None:
        self.host = host
        self.port = port
        self.max_message_size = max_message_size
        self.timeout_ms = timeout_ms

        self.is_connected = False
        self.locking_event = asyncio.Event()
        self.locking_event.set()
        self.logger = getLogger(self.__class__.__name__)

    async def connect(self) -> None:
        if self.is_connected:
            return

        try:
            self.reader, self.writer = await open_connection(
                host=self.host,
                port=self.port,
                limit=self.max_message_size,
            )
        except ConnectionRefusedError as error:
            raise ClientFatalError.from_base_exception(error) from error

    async def send(self, request: Request) -> Response:
        request.trace_id = str(uuid4())

        await self.locking_event.wait()
        self.locking_event.set()

        try:
            self.writer.write(request.dump() + MESSAGE_SEPARATOR)
            await self.writer.drain()
            data = await self.reader.readuntil(MESSAGE_SEPARATOR)
        except (
            ConnectionRefusedError,
            LimitOverrunError,
        ) as error:
            raise ClientFatalError.from_base_exception(error) from error

        self.locking_event.clear()

        return Response.load(data[:-1])
