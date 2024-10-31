from collections.abc import Awaitable, Callable
from typing import Self

from shiny_rpc.errors import (
    MethodInternalError,
    UnknownMethodError,
    ValidationError,
)
from shiny_rpc.ifaces import UserIface
from shiny_rpc.messages import (
    Request,
    Response,
    response_from_error,
)

type HandlerMethod = Callable[[Request, UserIface], Awaitable[Response]]


class MessageHandler:
    methods: dict[str, HandlerMethod]

    def __init__(self) -> None:
        self.methods = {}

    def include(
        self,
        message_handler: Self,
    ) -> None:
        self.methods.update(message_handler.methods)

    def add_method(
        self,
        method_name: str,
        func: HandlerMethod,
    ) -> None:
        self.methods[method_name] = func

    def method(
        self,
        method_name: str,
    ) -> Callable[[HandlerMethod], HandlerMethod]:
        def decorator(func: HandlerMethod) -> HandlerMethod:
            self.add_method(
                method_name=method_name,
                func=func,
            )

            return func
        return decorator

    async def handle(
        self,
        message: bytes,
        user: UserIface,
    ) -> Response:
        try:
            method_name = Request.find_method_name(message)
        except ValidationError as error:
            return response_from_error(error)

        method = self.methods.get(method_name)
        if not method or method_name not in self.methods:
            return response_from_error(UnknownMethodError(method_name))

        request_class = self.methods[method_name].__annotations__.get('request')
        if not request_class:
            return response_from_error(
                MethodInternalError(
                    details={'request_argument': 'must be set in message handler method'},
                ),
            )

        try:
            request = request_class.load(message)
        except ValidationError as error:
            return response_from_error(error)

        try:
            return await method(request, user)
        except BaseException as error:  # noqa: BLE001
            return response_from_error(
                MethodInternalError.from_base_exception(error),
            )
