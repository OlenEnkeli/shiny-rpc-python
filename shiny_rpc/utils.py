import logging
import re
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from rich import print
from rich.logging import RichHandler

from shiny_rpc.types import SyncFunction

AVERAGE_TEST_COUNT = 10


def check_camel_case(validated: str) -> bool:
    return bool(re.match('^([A-Z][a-z]+)+$', validated))


def to_camel_case(snake_str: str) -> str:
    return ''.join(x.capitalize() for x in snake_str.lower().split('_'))


def time_it(
    function: SyncFunction,
) -> SyncFunction:
    @wraps(function)
    def wrapper(
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> Any:  # noqa:ANN401
        started_at = datetime.now(tz=UTC)
        result = function(*args, **kwargs)
        finished_at = datetime.now(tz=UTC)

        raw_duration = finished_at - started_at
        duration = float(raw_duration.seconds + raw_duration.microseconds / 1000)

        print(
            f'[ocean_blue4][TIME][/ocean_blue4] Function [turquoise4][bold]{function.__name__}[/bold][/turquoise4]'
            f'finished at [medium_spring_green][bold]{duration}[/medium_spring_green]sec[/bold]',
        )

        return result
    return wrapper


def compute_average_time(
    function: SyncFunction,
) -> SyncFunction:
    @wraps(function)
    def wrapper(
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> Any:  # noqa:ANN401
        started_at = datetime.now(tz=UTC)
        result = None

        for _ in range(AVERAGE_TEST_COUNT):
            result = function(*args, **kwargs)

        finished_at = datetime.now(tz=UTC)

        raw_duration = finished_at - started_at
        duration = float(raw_duration.seconds + raw_duration.microseconds / 1000)

        raw_average_duration = raw_duration / AVERAGE_TEST_COUNT
        average_duration = float(raw_average_duration.seconds + raw_average_duration.microseconds / 1000)

        print(
            f'[steel_blue1][TIME][/steel_blue1] Function [turquoise4][bold]{function.__name__}[/bold][/turquoise4]:\n'
            f' - Average \t [medium_spring_green][bold]{average_duration}[/bold] sec[/medium_spring_green]\n'
            f' - Total \t [medium_spring_green][bold]{duration}[/bold] sec[/medium_spring_green]\n',
        )

        return result
    return wrapper


def get_class_methods(cls: object) -> list[str]:
    return [
        attribute
        for attribute in dir(cls)
        if callable(getattr(cls, attribute))
        and attribute.startswith('_') is False
    ]


def setup_rich_logging() -> None:
    logging.basicConfig(
        level='DEBUG',
        datefmt='[%X]',
        format='%(message)s',
        handlers=[
            RichHandler(
                omit_repeated_times=False,
                show_level=True,
                rich_tracebacks=True,
            ),
        ],
    )
