from examples.todo_list.requests import CreateTaskRequest
from examples.todo_list.responses import CreateTaskResponse
from shiny_rpc.user import User


async def create_task(
    request: CreateTaskRequest,
    user: User,
) -> CreateTaskResponse:
    raise NotImplementedError
