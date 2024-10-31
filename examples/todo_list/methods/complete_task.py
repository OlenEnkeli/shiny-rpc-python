from examples.todo_list.requests import CompleteTaskRequest
from examples.todo_list.responses import CompleteTaskResponse
from shiny_rpc.user import User


async def complete_task(
    request: CompleteTaskRequest,
    user: User,
) -> CompleteTaskResponse:
    raise NotImplementedError
