import asyncio

from shiny_rpc.ifaces import UserIface


class User(UserIface):
    address: str
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __init__(
        self,
        address: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self.address = address
        self.reader = reader
        self.writer = writer
