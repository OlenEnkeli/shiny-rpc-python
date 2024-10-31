
from shiny_rpc.schema import BasePayloadSchema

from .base import BaseResponse
from .dtos import TaskDTO, TodoListDTO


class CreateTodoListResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        list: TodoListDTO


class GetTodoListResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        list: TodoListDTO


class UpdateTodoListResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        list: TodoListDTO


class DeleteTodoListResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        list: TodoListDTO


class CreateTaskResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        task: TaskDTO


class UpdateTaskResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        task: TaskDTO


class CompleteTaskResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        task: TaskDTO


class IncreaseTaskCompletionPercentResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        task: TaskDTO


class DeleteTaskResponse(BaseResponse):
    class PayloadSchema(BasePayloadSchema):
        task: TaskDTO


