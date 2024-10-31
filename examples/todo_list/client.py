from shiny_rpc.client import BaseClient

from .requests import (
    CompleteTaskRequest,
    CreateTaskRequest,
    CreateTodoListRequest,
    DeleteTaskRequest,
    DeleteTodoListRequest,
    GetTodoListRequest,
    IncreaseTaskCompletionPercentRequest,
    UpdateTaskRequest,
    UpdateTodoListRequest,
)
from .responses import (
    CompleteTaskResponse,
    CreateTaskResponse,
    CreateTodoListResponse,
    DeleteTaskResponse,
    DeleteTodoListResponse,
    GetTodoListResponse,
    IncreaseTaskCompletionPercentResponse,
    UpdateTaskResponse,
    UpdateTodoListResponse,
)


class Client(BaseClient):
    async def create_todo_list(
        self,
        payload: CreateTodoListRequest.PayloadSchema,
        headers: CreateTodoListRequest.HeadersSchema | None = None,
    ) -> CreateTodoListResponse:
        return await self.send(  # type:ignore[return-value]
            CreateTodoListRequest(
                method_name='create_todo_list',
                payload=payload,
                headers=headers,
            ),
        )

    async def get_todo_list(
        self,
        payload: GetTodoListRequest.PayloadSchema,
        headers: GetTodoListRequest.HeadersSchema | None = None,
    ) -> GetTodoListResponse:
        return await self.send(  # type:ignore[return-value]
            GetTodoListRequest(
                method_name='get_todo_list',
                payload=payload,
                headers=headers,
            ),
        )

    async def update_todo_list(
        self,
        payload: UpdateTodoListRequest.PayloadSchema,
        headers: UpdateTodoListRequest.HeadersSchema | None = None,
    ) -> UpdateTodoListResponse:
        return await self.send(  # type:ignore[return-value]
            UpdateTodoListRequest(
                method_name='update_todo_list',
                payload=payload,
                headers=headers,
            ),
        )

    async def delete_todo_list(
        self,
        payload: DeleteTodoListRequest.PayloadSchema,
        headers: DeleteTodoListRequest.HeadersSchema | None = None,
    ) -> DeleteTodoListResponse:
        return await self.send(  # type:ignore[return-value]
            DeleteTodoListRequest(
                method_name='delete_todo_list',
                payload=payload,
                headers=headers,
            ),
        )

    async def create_task(
        self,
        payload: CreateTaskRequest.PayloadSchema,
        headers: CreateTaskRequest.HeadersSchema | None = None,
    ) -> CreateTaskResponse:
        return await self.send(  # type:ignore[return-value]
            CreateTaskRequest(
                method_name='create_task',
                payload=payload,
                headers=headers,
            ),
        )

    async def update_task(
        self,
        payload: UpdateTaskRequest.PayloadSchema,
        headers: UpdateTaskRequest.HeadersSchema | None = None,
    ) -> UpdateTaskResponse:
        return await self.send(  # type:ignore[return-value]
            UpdateTaskRequest(
                method_name='update_task',
                payload=payload,
                headers=headers,
            ),
        )

    async def complete_task(
        self,
        payload: CompleteTaskRequest.PayloadSchema,
        headers: CompleteTaskRequest.HeadersSchema | None = None,
    ) -> CompleteTaskResponse:
        return await self.send(  # type:ignore[return-value]
            CompleteTaskRequest(
                method_name='complete_task',
                payload=payload,
                headers=headers,
            ),
        )

    async def increase_task_completion_percent(
        self,
        payload: IncreaseTaskCompletionPercentRequest.PayloadSchema,
        headers: IncreaseTaskCompletionPercentRequest.HeadersSchema | None = None,
    ) -> IncreaseTaskCompletionPercentResponse:
        return await self.send(  # type:ignore[return-value]
            IncreaseTaskCompletionPercentRequest(
                method_name='increase_task_completion_percent',
                payload=payload,
                headers=headers,
            ),
        )

    async def delete_task(
        self,
        payload: DeleteTaskRequest.PayloadSchema,
        headers: DeleteTaskRequest.HeadersSchema | None = None,
    ) -> DeleteTaskResponse:
        return await self.send(  # type:ignore[return-value]
            DeleteTaskRequest(
                method_name='delete_task',
                payload=payload,
                headers=headers,
            ),
        )



# WARNING! It`s just example. Please, use some settings class for client bootstrapping.

client = Client(
    host='127.0.0.1',
    port=7777,
)
