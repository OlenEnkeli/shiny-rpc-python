from examples.todo_list.requests import CreateTodoListRequest
from examples.todo_list.responses import CreateTodoListResponse
from shiny_rpc.user import User


async def create_todo_list(
    request: CreateTodoListRequest,
    user: User,
) -> CreateTodoListResponse:
    raise NotImplementedError
