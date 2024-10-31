from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM as PSQL_ENUM
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
)

from .types import datetime_timezone


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            datetime_timezone: DateTime(timezone=True),
            Enum: PSQL_ENUM(),
            UUID: PSQL_UUID(),
        },
    )

    created_at: Mapped[datetime_timezone] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=UTC),
    )
    updated_at: Mapped[datetime_timezone | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )
