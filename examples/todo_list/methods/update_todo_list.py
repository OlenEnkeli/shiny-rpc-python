from examples.todo_list.requests import UpdateTodoListRequest
from examples.todo_list.responses import UpdateTodoListResponse
from shiny_rpc.user import User


async def update_todo_list(
    request: UpdateTodoListRequest,
    user: User,
) -> UpdateTodoListResponse:
    raise NotImplementedError
