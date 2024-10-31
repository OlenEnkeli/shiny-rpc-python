import logging
import sys
from pathlib import Path
from typing import Any, Self


class BaseError(Exception):
    error_code: str
    details: dict[str, Any]
    log_level: int

    def __init__(
        self,
        *,
        error_code: str,
        details: dict[str, Any] | None = None,
        log_level: int = logging.WARNING,
    ) -> None:
        self.error_code = error_code
        self.log_level = log_level
        self.details = {
            'error_code': self.error_code,
            'details': details or {},
        }

    @property
    def is_fatal(self) -> bool:
        return self.log_level == logging.CRITICAL

    def __str__(self) -> str:
        return f'{self.error_code}: {self.details}'

    @classmethod
    def from_base_exception(
        cls,
        exception: BaseException,
        *args: list[str],
        **kwargs: dict[str, Any],
    ) -> Self:
        return cls(
            *args,
            details={
                'exception': exception.__class__.__name__,
                'exception_message': str(exception),
            },
            **kwargs, # type:ignore[arg-type]
        )


class FatalError(BaseError):
    def __init__(
        self,
        error_code: str,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code=error_code,
            details=details,
            log_level=logging.CRITICAL,
        )


class ServerFatalError(FatalError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='ServerFatalError',
            details=details,
        )


class ClientFatalError(FatalError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='ClientServerError',
            details=details,
        )


class RequestTimeoutError(BaseError):
    def __init__(
        self,
        timeout: int,
    ) -> None:
        super().__init__(
            error_code='RequestTimeout',
            details={
                'timeout': timeout,
            },
        )


class ExternalError(BaseError):
    ...


def handle_error(
    logger: logging.Logger,
    error: BaseError,
    log_level: int,
    *,
    exit_if_fatal: bool = False,
) -> None:
    if exit_if_fatal and error.is_fatal:
        logger.error(error)
        logger.error('Exiting')
        sys.exit(1)

    if log_level > error.log_level:
        return

    match error.log_level:
        case logging.CRITICAL:
            logger.critical(error)
        case logging.ERROR:
            logger.error(error)
        case logging.WARNING:
            logger.warning(error)
        case _:
            logger.warning(error)


class ValidationError(ExternalError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='ValidationError',
            details=details,
        )


class InvalidMessageFormatError(ValidationError):
    def __init__(self) -> None:
        super().__init__(
            details={
                'invalid_message_format': 'please check shiny_rpc request/response format documentation',
            },
        )


class UnknownMethodError(ExternalError):
    def __init__(
        self,
        method_name: str,
    ) -> None:
        super().__init__(
            error_code='UnknownMethod',
            details={'method': method_name},
        )


class MethodInternalError(ExternalError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='MethodInternal',
            details=details,
        )


class MaxMessageSizeReceivedError(ExternalError):
    def __init__(
        self,
        max_message_size: int,
    ) -> None:
        super().__init__(
            error_code='MaxMessageSizeReceived',
            details={
                'max_message_size': max_message_size,
            },
        )


class AnnotationError(FatalError):
    ...


class AnnotationValidationError(AnnotationError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='AnnotationValidation',
            details=details,
        )


class AnnotationUnknownFieldTypeError(AnnotationError):
    def __init__(
        self,
        field_type: str,
    ) -> None:
        super().__init__(
            error_code = 'AnnotationUnknownFieldType',
            details = {
                'unknown_field_type': field_type,
            },
        )


class AnnotationCaseError(AnnotationValidationError):
    def __init__(
        self,
        field: str,
        *,
        upper: bool = True,
    ) -> None:
        super().__init__(
            details={
                field: f'must be in {'camelCase or UpperCase' if upper else 'lower_case'}',
            },
        )


class AnnotationEnumNotFoundError(AnnotationValidationError):
    def __init__(
        self,
        field: str,
    ) -> None:
        super().__init__(
            details={
                'not_found': f'{field} enum',
            },
        )


class AnnotationObjectNotFoundError(AnnotationValidationError):
    def __init__(
        self,
        field: str,
    ) -> None:
        super().__init__(
            details={
                'not_found': f'{field} object',
            },
        )


class AnnotationNoMethodError(AnnotationError):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            error_code='AnnotationNoMethod',
            details={
                'no_method': 'at least one must be declared in annotation file',
            },
        )


class AnnotationCantOpenFileError(AnnotationError):
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        super().__init__(
            error_code='AnnotationCantOpenFile',
            details={
                'file_path': file_path,
            },
        )


class AnnotationParseError(AnnotationError):
    def __init__(
        self,
        details: dict[str, Any],
    ) -> None:
        super().__init__(
            error_code='AnnotationParseError',
            details=details,
        )


