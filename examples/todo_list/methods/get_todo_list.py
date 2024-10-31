from examples.todo_list.requests import GetTodoListRequest
from examples.todo_list.responses import GetTodoListResponse
from shiny_rpc.user import User


async def get_todo_list(
    request: GetTodoListRequest,
    user: User,
) -> GetTodoListResponse:
    raise NotImplementedError
