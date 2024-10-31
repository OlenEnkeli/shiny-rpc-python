from shiny_rpc.message_hander import MessageHandler

from . import (
    complete_task,
    create_task,
    create_todo_list,
    delete_task,
    delete_todo_list,
    get_todo_list,
    increase_task_completion_percent,
    update_task,
    update_todo_list,
)

handler = MessageHandler()


handler.add_method(
    method_name='create_todo_list',
    func=create_todo_list,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='get_todo_list',
    func=get_todo_list,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='update_todo_list',
    func=update_todo_list,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='delete_todo_list',
    func=delete_todo_list,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='create_task',
    func=create_task,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='update_task',
    func=update_task,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='complete_task',
    func=complete_task,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='increase_task_completion_percent',
    func=increase_task_completion_percent,  # type:ignore[arg-type]
)
handler.add_method(
    method_name='delete_task',
    func=delete_task,  # type:ignore[arg-type]
)
