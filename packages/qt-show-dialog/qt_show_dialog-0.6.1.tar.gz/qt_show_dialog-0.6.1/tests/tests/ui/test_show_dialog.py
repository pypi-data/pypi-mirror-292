from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from pytest_params import params

from src.show_dialog import ExitCode, Inputs, ShowDialog
from tests.libs import config


@pytest.fixture(scope='session')
def app():
    _app = QApplication([])
    yield _app


@pytest.fixture
def show_dialog(request, app, qtbot):
    inputs = getattr(request, 'param', Inputs())
    dialog = ShowDialog(app, inputs)
    qtbot.addWidget(dialog)

    yield dialog


@params('show_dialog', [('dialog title', Inputs(dialog_title='foo bar'))], indirect=True)
def test_dialog_title(show_dialog: ShowDialog):
    assert show_dialog.windowTitle() == 'foo bar'


@params('show_dialog', [('simple title', Inputs(title='foo bar'))], indirect=True)
def test_title(show_dialog: ShowDialog):
    assert show_dialog.title_label.text() == 'foo bar'


@params('show_dialog', [('simple description', Inputs(description='foo bar'))], indirect=True)
def test_description(show_dialog: ShowDialog):
    assert show_dialog.description_label.text() == 'foo bar'


@params(
    'show_dialog',
    [
        ('markdown description', Inputs(description='# Title\ntext', description_md=True)),
    ],
    indirect=True,
)
def test_description_md(show_dialog: ShowDialog):
    assert show_dialog.description_label.text() == '<h1>Title</h1>\n<p>text</p>'


@params(
    'show_dialog, expected_description',
    [
        (
            'single line',
            Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_02.yaml'),
            'This multiline text will transform into a single line.',
        ),
        (
            'single line, newline at end',
            Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_03.yaml'),
            'This multiline text will transform into a single line.\n',
        ),
        (
            'multi line',
            Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_04.yaml'),
            'This multiline text will\nretain its original newlines.',
        ),
        (
            'multi line, newline at end',
            Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_05.yaml'),
            'This multiline text will\nretain its original newlines.\n',
        ),
    ],
    indirect=['show_dialog'],
)
def test_description_multi_lines(show_dialog: ShowDialog, expected_description: str):
    assert show_dialog.description_label.text() == expected_description


@patch('PySide6.QtWidgets.QApplication.exit')
def test_pass_clicked(exit_mock, show_dialog: ShowDialog):
    """Clicking PASS button application exits with code 0."""
    QTest.mouseClick(show_dialog.pass_button, Qt.MouseButton.LeftButton)
    exit_mock.assert_called_once_with(ExitCode.Pass)


@patch('PySide6.QtWidgets.QApplication.exit')
def test_fail_clicked(exit_mock, show_dialog: ShowDialog):
    """Clicking FAIL button application exits with code 1."""
    QTest.mouseClick(show_dialog.fail_button, Qt.MouseButton.LeftButton)
    exit_mock.assert_called_once_with(ExitCode.Fail)


@pytest.mark.skip('Not working.')
@patch('PySide6.QtWidgets.QApplication.exit')
def test_pass_shortcut(exit_mock, show_dialog: ShowDialog):
    # key_event_press = QKeyEvent(
    #     QKeyEvent.Type.KeyPress, Qt.Key.Key_Q, Qt.KeyboardModifier.ControlModifier
    # )
    # key_event_release = QKeyEvent(
    #     QKeyEvent.Type.KeyRelease, Qt.Key.Key_Q, Qt.KeyboardModifier.ControlModifier
    # )
    #
    # show_dialog.app.postEvent(show_dialog, key_event_press)
    # show_dialog.app.postEvent(show_dialog, key_event_release)

    QTest.keyClick(show_dialog, Qt.Key.Key_P, Qt.KeyboardModifier.ControlModifier)
    exit_mock.assert_called_once_with(ExitCode.Pass)


@params(
    'show_dialog, expected_pass_fail_text',
    [
        (
            'custom text on buttons',
            Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_06.yaml'),
            ('Ok', 'Cancel'),
        ),
    ],
    indirect=['show_dialog'],
)
def test_pass_fail_buttons_text(show_dialog: ShowDialog, expected_pass_fail_text: tuple[str, str]):
    assert show_dialog.pass_button.text() == expected_pass_fail_text[0]
    assert show_dialog.fail_button.text() == expected_pass_fail_text[1]


@params(
    'show_dialog',
    [
        ('no timeout - default', Inputs()),
        ('no timeout - set to 0', Inputs(timeout=0)),
    ],
    indirect=True,
)
def test_timeout_no_timeout(show_dialog: ShowDialog):
    """Timeout UI should not appear if there's no timeout."""
    assert not show_dialog.timeout_progress_bar.isVisible()
    assert not show_dialog.timeout_increase_button.isVisible()
