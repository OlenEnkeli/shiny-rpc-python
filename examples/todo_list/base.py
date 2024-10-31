from uuid import UUID

from shiny_rpc.messages import Request, Response
from shiny_rpc.schema import BaseHeadersSchema


class CommonHeadersSchema(BaseHeadersSchema):
    service_id: UUID


class BaseRequest(Request):
    class HeadersSchema(CommonHeadersSchema):
        ...


class BaseResponse(Response):
    class HeadersSchema(CommonHeadersSchema):
        ...
