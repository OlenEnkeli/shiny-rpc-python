import asyncio
from abc import ABC, abstractmethod


class UserIface(ABC):
    address: str
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    @abstractmethod
    def __init__(
        self,
        address: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        ...
