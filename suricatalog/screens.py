"""
Screen logic
"""
import sys
from traceback import StackSummary

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Pretty, Button

from suricatalog import BASEDIR


class DetailScreen(ModalScreen):
    """
    Detail screen for an event
    """
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = BASEDIR.joinpath('css').joinpath('details_screen.tcss')

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            data: str = None
    ):
        """
        Detail screen constructor
        :param name:
        :param ident:
        :param classes:
        :param data:
        """
        super().__init__(name, ident, classes)
        self.data = data

    def compose(self) -> ComposeResult:
        """
        Populate screen component with data
        :return:
        """
        yield Pretty(self.data)
        button = Button("Close", variant="primary", id="close")
        button.tooltip = "Go back to main screen"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        """
        Handle exit button
        :param _:
        :return:
        """
        self.app.pop_screen()


class ErrorScreen(ModalScreen):
    """
    Specialized error screen
    """
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = BASEDIR.joinpath('css').joinpath('details_screen.tcss')

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            data: str = None,
            trace: StackSummary = None,
            reason: str = None
    ):
        """
        Screen constructor
        :param name:
        :param ident:
        :param classes:
        :param data:
        :param trace:
        :param reason:
        """
        super().__init__(name, ident, classes)
        self.data = data
        self.trace = trace
        self.reason = reason

    def compose(self) -> ComposeResult:
        """
        Populate UI components with data
        :return:
        """
        if self.trace and self.reason:
            yield Pretty(
                {
                    'reason': self.reason,
                    'traceback': self.trace
                }
            )
        self.notify(
            title="Unrecoverable error, press 'E' to exit!",
            message="There was an error, application won't recover.",
            severity="error",
            timeout=15
        )
        button = Button.error(
            "Exit application",
            id="close"
        )
        button.tooltip = "Unable to load data, program will exit!"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        """
        Handle pressed close button
        :param _:
        :return:
        """
        sys.exit(100)
