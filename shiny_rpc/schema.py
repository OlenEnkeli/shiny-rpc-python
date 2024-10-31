from collections.abc import Iterable
from typing import Any, Self

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def model_validate_list(cls, objs: Iterable[Any]) -> list[Self]:
        return [
            cls.model_validate(obj=obj)
            for obj in objs
        ]


class BasePayloadSchema(BaseSchema):
    ...


class BaseHeadersSchema(BaseSchema):
    trace_id: str | None = None
