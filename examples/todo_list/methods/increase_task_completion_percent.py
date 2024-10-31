from examples.todo_list.requests import IncreaseTaskCompletionPercentRequest
from examples.todo_list.responses import IncreaseTaskCompletionPercentResponse
from shiny_rpc.user import User


async def increase_task_completion_percent(
    request: IncreaseTaskCompletionPercentRequest,
    user: User,
) -> IncreaseTaskCompletionPercentResponse:
    raise NotImplementedError
