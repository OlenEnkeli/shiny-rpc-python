from collections.abc import Callable, Coroutine
from typing import Any

type SyncFunction = Callable[..., Any]
type AsyncFunction = Callable[..., Coroutine[Any, Any, Any]]

