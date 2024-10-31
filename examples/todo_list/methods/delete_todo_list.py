from examples.todo_list.requests import DeleteTodoListRequest
from examples.todo_list.responses import DeleteTodoListResponse
from shiny_rpc.user import User


async def delete_todo_list(
    request: DeleteTodoListRequest,
    user: User,
) -> DeleteTodoListResponse:
    raise NotImplementedError
