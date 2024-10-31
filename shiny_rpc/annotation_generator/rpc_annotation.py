from enum import StrEnum
from typing import Any, Literal

from shiny_rpc.errors import (
    AnnotationCaseError,
    AnnotationNoMethodError,
    AnnotationUnknownFieldTypeError,
    AnnotationValidationError,
)
from shiny_rpc.schema import BaseSchema
from shiny_rpc.utils import check_camel_case

from .types import AnnotationField, FieldType

FIELD_TYPE_PRIMITIVES = [
    'int',
    'float',
    'boolean',
    'string',
    'date',
    'datetime',
    'uuid',
    'null',
]
FIELD_TYPE_PRIMITIVES_TO_PYTHON_TYPES = {
    'int': 'int',
    'float': 'float',
    'boolean': 'bool',
    'string': 'str',
    'date': 'date',
    'datetime': 'datetime',
    'uuid': 'UUID',
    'null': 'None',
}


type FieldTypePrimitive = (
    Literal[
        'int',
        'float',
        'boolean',
        'string',
        'date',
        'datetime',
        'uuid',
        'null',
    ]
    | StrEnum
    | str
)
type RawFieldType = FieldTypePrimitive | list[RawFieldType | list[RawFieldType]]


class AnnotationSchema(BaseSchema):
    enums: dict[str, dict[str, str]] | None = None
    objects: dict[str, dict[str, Any]] | None = None
    methods: dict[str, dict[str, dict[str, Any]]] | None = None
    headers: dict[str, Any] | None = None


class RPCAnnotationMethod:
    request: dict[str, AnnotationField]
    response: dict[str, RawFieldType]

    def __init__(self) -> None:
        self.request = {}
        self.response = {}


class RPCAnnotationDTO:
    schema: AnnotationSchema
    enums: dict[str, StrEnum]
    objects: dict[str, dict[str, AnnotationField]]
    methods: dict[str, RPCAnnotationMethod]
    headers: dict[str, AnnotationField]

    def __init__(self, annotation_schema: AnnotationSchema) -> None:
        self.schema = annotation_schema
        self.enums = {}
        self.objects = {}
        self.methods = {}
        self.headers = {}

        self._make()

    def _make_enums(self) -> None:
        if not self.schema.enums:
            return

        for enum_key, raw_enum in self.schema.enums.items():
            if not check_camel_case(enum_key):
                raise AnnotationCaseError(f'enums.{enum_key}')

            self.enums[enum_key] = StrEnum(
                enum_key,
                raw_enum.items(),
            )

    @staticmethod
    def _convert_field_value_to_python_type(field_type: str) -> str:
        if field_type not in FIELD_TYPE_PRIMITIVES_TO_PYTHON_TYPES:
            raise AnnotationUnknownFieldTypeError(field_type)

        return FIELD_TYPE_PRIMITIVES_TO_PYTHON_TYPES[field_type]

    def _convert_field_value(
        self,
        field_value: str | list[str | list[str]],
    ) -> AnnotationField:
        if isinstance(field_value, list):
            if len(field_value) == 1:
                return AnnotationField(
                    field_type=FieldType.LIST,
                    value=self._convert_field_value(field_value[0]),  # type:ignore[arg-type]
                )

            return AnnotationField(
                field_type=FieldType.OR,
                value=[
                    self._convert_field_value(current_value)  # type:ignore[arg-type]
                    for current_value in field_value
                ],
            )

        if field_value in self.enums:
            return AnnotationField(
                field_type=FieldType.ENUM,
                value=field_value,
            )

        if field_value in self.objects:
            return AnnotationField(
                field_type=FieldType.OBJECT,
                value=field_value,
            )

        if field_value in FIELD_TYPE_PRIMITIVES:
            return AnnotationField(
                field_type=FieldType.PRIMITIVE,
                value=self._convert_field_value_to_python_type(field_value),
            )

        raise AnnotationValidationError(
            details={
                'unknown_signature': field_value,
            },
        )

    def _make_objects(self) -> None:
        if not self.schema.objects:
            return

        for object_key, raw_object in self.schema.objects.items():
            if not check_camel_case(object_key):
                raise AnnotationCaseError(f'objects.{object_key}')

            self.objects[object_key] = {}

            for key, value in raw_object.items():
                self.objects[object_key][key] = self._convert_field_value(value)

    def _make_methods(self) -> None:
        if not self.schema.methods:
            raise AnnotationNoMethodError

        for method_key, raw_method in self.schema.methods.items():
            if not method_key.islower():
                raise AnnotationCaseError(
                    field=f'methods.{method_key}',
                    upper=False,
                )

            if 'request' not in raw_method or 'response' not in raw_method:
                raise AnnotationValidationError(
                    details={
                        'request_or_response_object': f'not found in {method_key} method',
                    },
                )

            self.methods[method_key] = RPCAnnotationMethod()

            for direction in ['request', 'response']:
                current_object = (
                    self.methods[method_key].request
                    if direction == 'request'
                    else self.methods[method_key].response
                )

                for key, value in raw_method[direction].items():
                    current_object[key] = self._convert_field_value(value)  # type:ignore[assignment]

    def _make_headers(self) -> None:
        if not self.schema.headers:
            return

        for key, value in self.schema.headers.items():
            self.headers[key] = self._convert_field_value(value)

    def _make(self) -> None:
        self._make_enums()
        self._make_objects()
        self._make_methods()
        self._make_headers()
