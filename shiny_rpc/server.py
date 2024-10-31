import asyncio
import logging
from typing import Any

from shiny_rpc.constants import MESSAGE_SEPARATOR
from shiny_rpc.errors import (
    BaseError,
    ExternalError,
    MaxMessageSizeReceivedError,
    ServerFatalError,
    handle_error,
)
from shiny_rpc.ifaces import UserIface
from shiny_rpc.message_hander import MessageHandler
from shiny_rpc.messages import Response, response_from_error
from shiny_rpc.user import User


class Server:
    message_handler: MessageHandler
    user_class: type[UserIface]

    host: str
    port: int
    connection_limit: int
    chunk_size: int
    max_message_size: int
    log_level: int
    log_messages: bool

    server: asyncio.Server
    users: dict[str, Any]


    def __init__(
        self,
        host: str,
        port: int,
        message_handler: MessageHandler,
        *,
        user_class: type[UserIface] = User,
        connection_limit: int = 2 ** 10,  # 1024
        chunk_size: int = 2**15,  # 32 KB
        max_message_size: int = 2**20,  # 1 MB
        log_level: int = logging.INFO,
        log_messages: bool = False,
    ) -> None:
        self.message_handler = message_handler
        self.user_class = user_class

        self.host = host
        self.port = port
        self.connection_limit = connection_limit
        self.chunk_size = chunk_size
        self.max_message_size = max_message_size
        self.log_level = log_level
        self.log_messages = log_messages

        self.users = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        if self.log_messages:
            self.logger.warning('Parameter log_messages is True. Use it only for debugging purposes!')

    def _handle_error(self, error: BaseError) -> None:
        return handle_error(
            log_level=self.log_level,
            error=error,
            logger=self.logger,
            exit_if_fatal=True,
        )

    def _make_user(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> User:
        address = writer.get_extra_info('peername')
        user_address = f'{address[0]}:{address[1]}'

        self.users[user_address] = self.user_class(
            address=user_address,
            reader=reader,
            writer=writer,
        )

        return self.users[user_address]

    async def _user_disconnected(self, user: User) -> None:
        self.logger.debug(f'User {user.address} was disconnected')

        user.writer.close()
        await user.writer.wait_closed()

        if user.address in self.users:
            self.users.pop(user.address)

    async def _send_response(self, user: User, response: Response) -> None:
        if user.address not in self.users:
            return

        try:
            user.writer.write(response.dump() + MESSAGE_SEPARATOR)
            await user.writer.drain()
        except BrokenPipeError:
            await self._user_disconnected(user)
            return

    async def _send_error(self, user: User, error: ExternalError) -> None:
        return await self._send_response(
            user=user,
            response=response_from_error(error),
        )

    async def _process_connection(
        self,
        user: User,
    ) -> None:
        data = await user.reader.readuntil(MESSAGE_SEPARATOR)

        response = await self.message_handler.handle(
            message=data[0:-1],
            user=user,
        )

        if self.log_messages:
            self.logger.debug(f'{user.address}: {response}')
            self.logger.debug(response.payload)

        await self._send_response(
            user=user,
            response=response,
        )

    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        user = self._make_user(
            reader=reader,
            writer=writer,
        )

        self.logger.debug(f'Connected user {user.address}')

        while True:
            try:
                await self._process_connection(user)

            except (
                ConnectionError,
                asyncio.IncompleteReadError,
            ):
                await self._user_disconnected(user)
                break

            except asyncio.LimitOverrunError:
                self.logger.debug(f'User {user.address} reach max message size')
                await self._send_error(
                    user=user,
                    error=MaxMessageSizeReceivedError(
                        max_message_size=self.max_message_size,
                    ),
                )
                await self._user_disconnected(user)
                break

    async def _connect(self) -> None:
        self.logger.info(f'Starting server on {self.host}:{self.port}')
        self.logger.info(f'Available methods: {list(self.message_handler.methods.keys())}')

        self.server = await asyncio.start_server(
            client_connected_cb=self._handle_connection,
            host=self.host,
            port=self.port,
            limit=self.max_message_size,
        )

    async def _run(self) -> None:
        await self._connect()

        async with self.server as server:
            await server.serve_forever()

    async def run(self) -> None:
        try:
            await self._run()
        except (
            OSError,
            KeyboardInterrupt,
            ServerFatalError,
            asyncio.CancelledError,
        ):
            self.logger.exception('Fatal error')
            self.logger.info('Exiting')
