import logging
import re
from typing import Any, Self
from uuid import uuid4

import orjson
from pydantic import ValidationError as PydanticValidationError

from shiny_rpc.constants import ZERO_TRACE_ID
from shiny_rpc.errors import (
    ExternalError,
    InvalidMessageFormatError,
    ValidationError,
)
from shiny_rpc.schema import BaseHeadersSchema, BasePayloadSchema
from shiny_rpc.utils import compute_average_time


class Request:
    method_name: str
    trace_id: str
    payload: BasePayloadSchema
    headers: BaseHeadersSchema

    class PayloadSchema(BasePayloadSchema):
        ...

    class HeadersSchema(BaseHeadersSchema):
        ...

    @property
    def headers_schema(self) -> type[BaseHeadersSchema]:
        return BaseHeadersSchema

    def __init__(
        self,
        method_name: str,
        trace_id: str | None = None,
        payload: dict[str, Any] | BasePayloadSchema | None = None,
        headers: dict[str, Any] | BaseHeadersSchema | None = None,
    ) -> None:
        payload = payload or {}
        headers = headers or {}

        self.method_name = method_name

        self.trace_id = trace_id or str(uuid4())
        if isinstance(headers, BaseHeadersSchema):
            headers.trace_id = self.trace_id
        else:
            headers['trace_id'] = self.trace_id

        if isinstance(payload, BasePayloadSchema):
            self.payload = payload
        else:
            try:
                self.payload = self.PayloadSchema.model_validate(payload)
            except PydanticValidationError as error:
                raise ValidationError.from_base_exception(error) from error

        if isinstance(headers, BaseHeadersSchema):
            self.headers = headers
        else:
            try:
                self.headers = self.HeadersSchema.model_validate(headers)
            except PydanticValidationError as error:
                raise ValidationError.from_base_exception(error) from error

    @classmethod
    def load(cls, data: bytes | str) -> Self:
        message = data if isinstance(data, str) else data.decode('utf-8')

        all_opening_curly_brace = [
            element.start()
            for element in re.finditer('(?={)', message)
        ]
        if len(all_opening_curly_brace) < 2:  # noqa:PLR2004
            raise InvalidMessageFormatError

        payload_start_at = all_opening_curly_brace[0]
        headers_start_at = all_opening_curly_brace[-1]

        if payload_start_at >= headers_start_at:
            raise InvalidMessageFormatError

        method_name = message[0:payload_start_at]

        try:
            payload = orjson.loads(message[payload_start_at:headers_start_at])
            headers = orjson.loads(message[headers_start_at:])
        except orjson.JSONDecodeError as error:
            raise ValidationError.from_base_exception(error) from error

        trace_id = headers.get('trace_id', None)

        return cls(
            method_name=method_name,
            payload=payload,
            headers=headers,
            trace_id=trace_id,
        )

    def dump(self) -> bytes:
        payload = orjson.dumps(self.PayloadSchema.model_dump(self.payload))
        headers = orjson.dumps(self.HeadersSchema.model_dump(self.headers))

        return b''.join([
            self.method_name.encode('utf-8'),
            payload,
            headers,
        ])

    @classmethod
    def find_method_name(cls, data: bytes | str) -> str:
        message = data if isinstance(data, str) else data.decode('utf-8')

        payload_start_at = message.find('{')
        if (
            payload_start_at in (-1, 0)
        ):
            raise InvalidMessageFormatError

        return message[0:payload_start_at]

    def __str__(self) -> str:
        return f'Request <{self.method_name}: {self.trace_id}>'


class Response:
    method_name: str
    trace_id: str
    payload: BasePayloadSchema
    headers: BaseHeadersSchema
    success: bool

    class PayloadSchema(BasePayloadSchema):
        ...

    class HeadersSchema(BaseHeadersSchema):
        ...

    def __init__(
        self,
        method_name: str,
        trace_id: str,
        *,
        success: bool,
        payload: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        self.method_name = method_name
        self.trace_id = trace_id
        self.success = success

        payload = payload or {}
        headers = headers or {}
        headers['trace_id'] = self.trace_id

        try:
            self.payload = self.PayloadSchema.model_validate(payload)
            self.headers = self.HeadersSchema.model_validate(headers)
        except PydanticValidationError as error:
            raise ValidationError.from_base_exception(error) from error

    @classmethod
    def load(cls, data: bytes | str) -> Self:
        message = data if isinstance(data, str) else data.decode('utf-8')

        success_start_at = message.find(':')
        if success_start_at < 2:  # noqa:PLR2004
            raise InvalidMessageFormatError

        all_opening_curly_brace = [
            element.start()
            for element in re.finditer('(?={)', message)
        ]
        if len(all_opening_curly_brace) < 2:  # noqa:PLR2004
            raise InvalidMessageFormatError

        payload_start_at = all_opening_curly_brace[0]
        headers_start_at = all_opening_curly_brace[-1]

        if payload_start_at >= headers_start_at:
            raise InvalidMessageFormatError

        if (
            success_start_at >= headers_start_at
            or payload_start_at >= headers_start_at
        ):
            raise InvalidMessageFormatError


        method_name = message[0:success_start_at]
        success = (message[success_start_at+1:payload_start_at] == 'ok')
        payload = orjson.loads(message[payload_start_at:headers_start_at])
        headers = orjson.loads(message[headers_start_at:])

        if not (trace_id := headers.get('trace_id')):
            raise InvalidMessageFormatError

        return cls(
            method_name=method_name,
            trace_id=trace_id,
            success=success,
            payload=payload,
            headers=headers,
        )

    def dump(self) -> bytes:
        payload = orjson.dumps(self.PayloadSchema.model_dump(self.payload))
        headers = orjson.dumps(self.HeadersSchema.model_dump(self.headers))
        success = b'ok' if self.success else b'err'

        return b''.join([
            self.method_name.encode('utf-8'),
            b':',
            success,
            payload,
            headers,
        ])

    def __str__(self) -> str:
        return f'Response[{'ok' if self.success else 'err'}] <{self.method_name}: {self.trace_id}>'


def response_from_error(
    error: ExternalError,
    request: Request | None = None,
) -> Response:
    return Response(
        method_name=(
            request.method_name
            if request
            else (
                '__error'
                if error.log_level in (logging.CRITICAL, logging.ERROR)
                else '__warning'
            )
        ),
        trace_id=request.trace_id if request else ZERO_TRACE_ID,
        success=False,
        payload={
            'error_code': error.error_code,
            'details': error.details,
        },
    )


if __name__ == '__main__':
    from rich import print

    from shiny_rpc.examples import (
        ExampleRequest,
        ExampleResponse,
        example_request_values,
        example_response_values,
    )

    @compute_average_time
    def make_request_response() -> tuple[Request, Response]:
        return (
            ExampleRequest(
                method_name='first_method',
                trace_id=str(uuid4()),
                payload=example_request_values,
            ),
            ExampleResponse(
                method_name='first_method',
                trace_id=str(uuid4()),
                success=True,
                payload=example_response_values,
            ),
        )

    req, resp = make_request_response()

    @compute_average_time
    def dump_request_response(request: ExampleRequest, response: ExampleResponse) -> tuple[bytes, bytes]:
        return (
            request.dump(),
            response.dump(),
        )

    dumped_req, dumped_resp = dump_request_response(req, resp)

    @compute_average_time
    def load_request_response(raw_request: bytes, raw_response: bytes) -> tuple[Request, Response]:
        return (
            ExampleRequest.load(raw_request),
            ExampleResponse.load(raw_response),
        )

    req, resp = load_request_response(dumped_req, dumped_resp)
    print(req, resp, sep='\n')
