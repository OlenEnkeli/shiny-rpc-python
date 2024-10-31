import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from rich import print
from rich.prompt import Prompt

from shiny_rpc.errors import AnnotationError
from shiny_rpc.utils import setup_rich_logging

from .annotation_generator import AnnotationGenerationMode, AnnotationGenerator


def main() -> None:
    setup_rich_logging()
    logger = logging.getLogger('AnnotationGenerator')

    print('✨  [deep_sky_blue2]Welcome to SmartRPC Python annotation code generator![/deep_sky_blue2]\n')

    parser = ArgumentParser()
    parser.add_argument(
        '-m',
        '--mode',
        default=None,
    )
    parser.add_argument(
        '-a',
        '--annotation_path',
        default=None,
    )
    parser.add_argument(
        '-t',
        '--target_path',
        default=None,
    )
    args = parser.parse_args()

    generation_mode: str = args.mode or Prompt.ask(
        prompt='Generation mode',
        default='full',
        choices=[
            'full',
            'client',
            'server',
        ],
        case_sensitive=False,
    )
    print(
        f' -> [deep_sky_blue2]{'Server and client' if generation_mode == 'full' else generation_mode.capitalize()}'
        f'[/deep_sky_blue2] will be generated',
    )

    annotation_path: str = args.annotation_path or Prompt.ask(
        prompt='Annotation JSON file path',
        default='examples/todo_list_annotation.json',
    )
    print(
        f' -> [deep_sky_blue2]Annotation path:[/deep_sky_blue2] {annotation_path}',
    )

    target_path: str = args.target_path or Prompt.ask(
        prompt='Target directory path',
        default='examples/todo_list',
    )
    print(
        f' -> [deep_sky_blue2]Target path:[/deep_sky_blue2] {target_path}',
    )

    print('\n🚢 Now [deep_sky_blue2]code generation[/deep_sky_blue2] in progress\n')

    try:
        generator = AnnotationGenerator(
            annotation_path=Path(annotation_path),
            target_path=Path(target_path),
            generation_mode=AnnotationGenerationMode[generation_mode.upper()],
        )
    except AnnotationError as error:
        logger.exception(error)
        sys.exit(1)

    generator.generate()

    print('\n🎇 [bold]Done![/bold]')
    print('📒 [bold]Please[/bold], don`t forget to [bold]lint[/bold] auto-generated code')

if __name__ == '__main__':
    main()
