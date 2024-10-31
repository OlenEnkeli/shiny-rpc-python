from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column

int_pkey = Annotated[
    int,
    mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    ),
]

uuid_pkey = Annotated[
    UUID,
    mapped_column(
        PSQL_UUID,
        primary_key=True,
        default=uuid4,
    ),
]

datetime_timezone = Annotated[datetime, True]
