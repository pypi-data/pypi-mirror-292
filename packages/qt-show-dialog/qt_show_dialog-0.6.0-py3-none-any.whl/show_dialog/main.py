import logging
import pprint
import sys
import types

from PySide6.QtWidgets import QApplication

from . import config
from .inputs import Inputs
from .ui.show_dialog import ShowDialog
from .utils_qt import list_resources, read_file


def show_dialog(inputs: Inputs, stylesheet: str = config.DEFAULT_STYLE):
    """
    Create an instance of ``ShowDialog`` and show it.
    """

    app = QApplication()
    window = ShowDialog(app, inputs, stylesheet)
    window.show()
    app_response = app.exec()
    if app_response != 0:
        logging.error(f'An error occurred. Exiting with status {app_response}.')
        sys.exit(app_response)


def _parse_args():
    """
    Parse CLI arguments.
    """
    from argparse import ArgumentParser, RawTextHelpFormatter

    from . import __version__

    description = f'Show Dialog {__version__}'

    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '--inputs',
        type=str,
        help='Input parameters in the form of a JSON string that maps to the `Inputs` class.\n'
        'If both `--inputs` and `--inputs-file` are specified, `--inputs` takes precedence.',
    )
    parser.add_argument(
        '--inputs-file',
        type=str,
        help='Path to JSON file that maps to the `Inputs` class.\n'
        'If both `--inputs` and `--inputs-file` are specified, `--inputs` takes precedence.',
    )
    parser.add_argument(
        '--stylesheet',
        type=str,
        default=config.DEFAULT_STYLE,
        help=f'Path to CSS file to apply. Can be a path to an external file or one of the included '
        f'{", ".join("`"+file+"`" for file in list_resources(":/stylesheets"))}',
    )
    parser.add_argument(
        '--log-level',
        # Can use `logging.getLevelNamesMapping()` instead of `_nameToLevel` on python 3.11+
        choices=[level.lower() for level in logging._nameToLevel],  # noqa
        default='info',
        help='Log level to use.',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )

    return parser.parse_args()


def _set_config_values(args) -> tuple[Inputs, str | None]:
    """
    Set ``config`` values.
    """
    from . import __version__

    logging.basicConfig(level=logging.getLevelName(args.log_level.upper()))
    logging.debug(
        f'Show Dialog.\n  App version: {__version__}\n  Log level: {args.log_level}\n  '
        f'File: {sys.executable}'
    )

    # Config contents
    config_dict = {
        key: getattr(config, key, '__UNDEFINED__')
        for key in sorted(dir(config))
        if (
            not key.startswith('_')
            and (  # noqa: W503
                type(getattr(config, key))
                not in [
                    types.FunctionType,
                    types.ModuleType,
                    type,
                ]
            )
        )
    }
    logging.debug('Config:\n' + '\n'.join(f'  {key}: {val}' for key, val in config_dict.items()))

    # Inputs
    inputs_json = args.inputs
    inputs_file = args.inputs_file

    if not (inputs_json or inputs_file):
        raise ValueError('Either `--inputs` or `--inputs-file` must be specified.')

    inputs = Inputs()
    if inputs_json:
        inputs = Inputs.from_json(inputs_json)
    if inputs_file:
        inputs_from_file = Inputs.from_file(inputs_file)
        if inputs_json:
            inputs = Inputs.from_dict(inputs_from_file.to_dict() | inputs.to_dict())
        else:
            inputs = inputs_from_file
    logging.debug(f'Inputs:\n{pprint.pformat(inputs.to_dict(), indent=2)}')

    css = None
    if args.stylesheet:
        css = read_file(args.stylesheet)

    return inputs, css


def main():
    _args = _parse_args()
    _inputs, _stylesheet = _set_config_values(_args)
    show_dialog(_inputs, _stylesheet)
    logging.debug('App exiting.')


if __name__ == '__main__':
    main()
