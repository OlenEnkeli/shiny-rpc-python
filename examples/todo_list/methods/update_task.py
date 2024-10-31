from examples.todo_list.requests import UpdateTaskRequest
from examples.todo_list.responses import UpdateTaskResponse
from shiny_rpc.user import User


async def update_task(
    request: UpdateTaskRequest,
    user: User,
) -> UpdateTaskResponse:
    raise NotImplementedError
