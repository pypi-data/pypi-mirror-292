from enum import IntEnum


class ExitCode(IntEnum):
    """
    App exit code.
    ``0`` represents success, otherwise failure.
    """

    Pass = 0
    """
    One of:

    * ``Pass`` button was clicked.
    * Timeout occurred but ``timeout_pass`` is ``True`` in inputs.
    * ``Ctrl+P`` shortcut was used.
    """
    Fail = 1
    """
    ``Fail`` button was clicked.
    """
    Cancel = 2
    """
    One of:

    * Dialog was closed with the ``X`` button.
    * ``Ctrl+Q`` shortcut was used.
    """
    Timeout = 3
    """
    Timeout occurred and ``timeout_pass`` is ``False`` in inputs.
    """
