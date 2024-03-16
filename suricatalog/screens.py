import sys
from traceback import FrameSummary

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Pretty, Button

from suricatalog import BASEDIR


class DetailScreen(ModalScreen):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = BASEDIR.joinpath('css').joinpath('details_screen.tcss')

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            data: str = None
    ):
        super().__init__(name, ident, classes)
        self.data = data

    def compose(self) -> ComposeResult:
        yield Pretty(self.data)
        button = Button("Close", variant="primary", id="close")
        button.tooltip = "Go back to main screen"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class ErrorScreen(ModalScreen):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = BASEDIR.joinpath('css').joinpath('details_screen.tcss')

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            data: str = None,
            trace: FrameSummary = None,
            reason: str = None
    ):
        super().__init__(name, ident, classes)
        self.data = data
        self.trace = trace
        self.reason = reason

    def compose(self) -> ComposeResult:
        if self.trace:
            yield Pretty(
                {
                    'reason': self.reason,
                    'traceback': self.trace
                }
            )
        button = Button.error("Exit application", id="close")
        button.tooltip = "Unable to load data, program will exit!"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        sys.exit(100)
