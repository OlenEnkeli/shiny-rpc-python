from examples.todo_list.requests import DeleteTaskRequest
from examples.todo_list.responses import DeleteTaskResponse
from shiny_rpc.user import User


async def delete_task(
    request: DeleteTaskRequest,
    user: User,
) -> DeleteTaskResponse:
    raise NotImplementedError
