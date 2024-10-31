
from shiny_rpc.schema import BasePayloadSchema

from .base import BaseRequest
from .enums import TaskTypeEnum


class CreateTodoListRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        title: str
        text: str
        user_id: int


class GetTodoListRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        id: int


class UpdateTodoListRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        id: int
        title: str
        text: str


class DeleteTodoListRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        id: int
        title: str
        text: str


class CreateTaskRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        task_list_id: int
        task_type: list[TaskTypeEnum]
        title: str
        text: str | None


class UpdateTaskRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        task_id: int
        title: str
        text: str | None


class CompleteTaskRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        task_id: int


class IncreaseTaskCompletionPercentRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        task_id: int
        delta: float


class DeleteTaskRequest(BaseRequest):
    class PayloadSchema(BasePayloadSchema):
        task_id: int


