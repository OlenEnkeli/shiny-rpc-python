from enum import Enum
from typing import Self

from shiny_rpc.errors import AnnotationUnknownFieldTypeError


class FieldType(str, Enum):
    ENUM = 'enum'
    OBJECT = 'object'
    PRIMITIVE = 'primitive'
    OR = 'or'
    LIST = 'list'


class AnnotationField:
    field_type: FieldType
    value: str | Self | list[Self]

    def __init__(
        self,
        field_type: FieldType,
        value: str | Self | list[Self],
    ) -> None:
        self.field_type = field_type
        self.value = value

    def render(self) -> str:
        if self.field_type == FieldType.OR:
            return ' | '.join(
                [
                    current_type.render()  # type:ignore[union-attr]
                    for current_type in self.value  # type:ignore[union-attr]
                ],
            )

        if self.field_type == FieldType.OBJECT:
            return f'{self.value}DTO'

        if self.field_type == FieldType.ENUM:
            return f'{self.value}Enum'

        if self.field_type == FieldType.LIST:
            return f'list[{self.value.render()}]'  # type:ignore[union-attr]

        if self.field_type == FieldType.PRIMITIVE:
            return str(self.value)

        raise AnnotationUnknownFieldTypeError(field_type=str(self.field_type))
