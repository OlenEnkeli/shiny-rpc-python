from datetime import datetime
from uuid import UUID

from shiny_rpc.schema import BaseSchema

from .enums import TaskTypeEnum


class TaskDTO(BaseSchema):
    id: int
    task_list_id: int
    task_type: list[TaskTypeEnum]
    is_completed: bool
    title: str
    text: str | None
    created_at: datetime
    completed_at: datetime | None
    completion_percent: float | None
    create_by_service: UUID | None


class TodoListDTO(BaseSchema):
    id: int
    title: str
    text: str
    created_at: datetime
    user_id: int
    is_closed: bool
    is_favourite: bool
    create_by_service: UUID | None


