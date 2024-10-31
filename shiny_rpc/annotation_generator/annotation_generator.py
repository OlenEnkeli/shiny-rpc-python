from enum import Enum
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
)
from pydantic import ValidationError
from rich import print

from shiny_rpc.errors import AnnotationCantOpenFileError, AnnotationParseError
from shiny_rpc.utils import to_camel_case

from .rpc_annotation import AnnotationSchema, RPCAnnotationDTO


class AnnotationGenerationMode(str, Enum):
    FULL = 'full'
    CLIENT = 'client'
    SERVER = 'server'


TEMPLATES_DIRECTORY = Path('shiny_rpc/annotation_generator/templates')


class AnnotationGenerator:
    target_path: Path
    package_name: str
    generation_type: AnnotationGenerationMode

    annotation_dto: RPCAnnotationDTO
    jinja_env: Environment

    def __init__(
        self,
        annotation_path: Path,
        *,
        generation_mode: AnnotationGenerationMode = AnnotationGenerationMode.FULL,
        target_path: Path = Path('code_generation_example'),
    ) -> None:
        self.target_path = target_path
        self.package_name = '.'.join(str(self.target_path).split('/'))
        self.generation_type = generation_mode

        self._setup_jinja()
        self._make_dto(annotation_path)
        self._make_directory()

    def _setup_jinja(self) -> None:
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIRECTORY),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        self.jinja_env.globals['to_camel_case'] = to_camel_case

    def _make_dto(
        self,
        annotation_path: Path,
    ) -> None:
        print('🌊 [bold]Parsing[/bold] annotation file')

        try:
            raw_content = annotation_path.read_text()
            schema = AnnotationSchema.model_validate_json(raw_content)
        except FileNotFoundError as error:
            raise AnnotationCantOpenFileError(annotation_path) from error
        except ValidationError as error:
            raise AnnotationParseError.from_base_exception(error) from error

        self.annotation_dto = RPCAnnotationDTO(schema)

        enums = list(self.annotation_dto.enums.keys())
        objects = self.annotation_dto.objects
        methods = list(self.annotation_dto.methods.keys())

        print(f' -> Enums[{len(enums)}]: {enums}')
        print(f' -> Objects[{len(objects)}]: {list(objects.keys())}')
        print(f' -> Methods[{len(methods)}]: {methods}\n')

    def _make_directory(self) -> None:
        if self.target_path.is_dir():
            print('[red]WARNING![/red] Target directory already exists.')
            return

        self.target_path.mkdir(parents=True, exist_ok=True)

    def _render(
        self,
        source_file_name: str,
        target_file_name: str,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        try:
            template = self.jinja_env.get_template(source_file_name)
        except TemplateNotFound as error:
            raise AnnotationCantOpenFileError(source_file_name) from error

        rendered = template.render(
            *args,
            dto=self.annotation_dto,
            package_name=self.package_name,
            **kwargs,
        )

        try:
            Path(self.target_path, target_file_name).write_text(rendered)
        except FileNotFoundError as error:
            raise AnnotationCantOpenFileError(target_file_name) from error

    @staticmethod
    def _print_step(file_name: str) -> None:
        print(f' -> [bold]Rendering[/bold] [code] {file_name} [/code]')

    def _generate_enums(self) -> None:
        file_name = 'enums.py'

        self._print_step(file_name)
        self._render(
            source_file_name='enums.py.jinja2',
            target_file_name=file_name,
        )

    def _generate_dtos(self) -> None:
        file_name = 'dtos.py'

        self._print_step(file_name)
        self._render(
            source_file_name='dtos.py.jinja2',
            target_file_name=file_name,
        )

    def _generate_baseclasses(self) -> None:
        file_name = 'base.py'

        self._print_step(file_name)
        self._render(
            source_file_name='base.py.jinja2',
            target_file_name=file_name,
        )

    def _make_requests_or_responses(
        self,
        *,
        is_request: bool,
    ) -> None:
        file_name = 'requests.py' if is_request else 'responses.py'

        self._print_step(file_name)
        self._render(
            source_file_name='requests_responses.py.jinja2',
            target_file_name=file_name,
            is_request=is_request,  # type:ignore[arg-type]
        )

    def _make_requests_and_responses(self) -> None:
        if self.generation_type == AnnotationGenerationMode.FULL:
            self._make_requests_or_responses(is_request=True)
            self._make_requests_or_responses(is_request=False)
        if self.generation_type == AnnotationGenerationMode.SERVER:
            self._make_requests_or_responses(is_request=False)
        if self.generation_type == AnnotationGenerationMode.CLIENT:
            self._make_requests_or_responses(is_request=True)

    def _make_server(self) -> None:
        if self.generation_type not in [AnnotationGenerationMode.FULL, AnnotationGenerationMode.SERVER]:
            return

        print(' -> [bold]Creating[/bold]  [code] methods [/code] directory')
        methods_path = Path(self.target_path, 'methods')

        if not methods_path.is_dir():
            methods_path.mkdir()

        for method_name in self.annotation_dto.methods:
            file_name = f'methods/{method_name}.py'

            self._print_step(file_name)
            self._render(
                source_file_name='method.py.jinja2',
                target_file_name=file_name,
                method_name=method_name,  # type:ignore[arg-type]
            )

        file_name = 'methods/__init__.py'

        self._print_step(file_name)
        self._render(
            source_file_name='methods_init.py.jinja2',
            target_file_name=file_name,
        )

        file_name = 'methods/handler.py'

        self._print_step(file_name)
        self._render(
            source_file_name='handler.py.jinja2',
            target_file_name=file_name,
        )

        file_name = 'server.py'

        self._print_step(file_name)
        self._render(
            source_file_name='server.py.jinja2',
            target_file_name=file_name,
        )

    def _make_client(self) -> None:
        if self.generation_type not in [AnnotationGenerationMode.FULL, AnnotationGenerationMode.CLIENT]:
            return

        file_name = 'client.py'

        self._print_step(file_name)
        self._render(
            source_file_name='client.py.jinja2',
            target_file_name=file_name,
        )

    def _make_init(self) -> None:
        self._print_step('__init__.py')

        file_path = Path(self.target_path, '__init__.py')
        file_path.touch()


    def generate(self) -> None:
        print('🐠 [bold]Rendering[/bold] files')

        self._generate_enums()
        self._generate_dtos()
        self._generate_baseclasses()
        self._make_requests_and_responses()
        self._make_server()
        self._make_client()
        self._make_init()

