"""
One shot application related code
"""
import traceback
from pathlib import Path

import pyperclip
from textual import work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Footer, Header, RichLog

from suricatalog.clipboard import copy_from_richlog
from suricatalog.filter import BaseFilter
from suricatalog.log import EveLogHandler
from suricatalog.screens import ErrorScreen


class OneShotApp(App):
    """
    One shot application, displays data based on filter
    """
    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("y,c", "copy_log", "Copy to clipboard")
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            eve: list[Path] = None,
            data_filter: BaseFilter = None
    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        :param eve:
        :param data_filter:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.data_filter = data_filter
        self.eve = eve
        self.loaded = 0

    def action_quit_app(self) -> None:
        """
        Exit application
        :return:
        """
        self.exit(f"Exiting {self.title} now...")

    def action_copy_log(self) -> None:
        """
        Copy contents to the clipboard
        :return:
        """
        rich_log = self.query_one(RichLog)
        try:
            _, ln = copy_from_richlog(rich_log)
            self.notify(f"Copied {ln} characters!", title="Copied selection")
        except pyperclip.PyperclipException as exc:
            # Show a toast popup if we fail to copy.
            self.notify(
                str(exc),
                title="Clipboard error",
                severity="error",
            )

    def compose(self) -> ComposeResult:
        """
        Place components of the app on screen
        :return:
        """
        yield Header()
        log = RichLog(
            id='events',
            highlight=True,
            auto_scroll=True
        )
        log.loading = True
        yield log
        yield Footer()

    async def pump_events(self, log: RichLog):
        """
        Get events from eve log and send them to the application log
        :param log:
        :return:
        """
        try:
            eve_lh = EveLogHandler()
            for single_alert in eve_lh.get_events(eve_files=self.eve, data_filter=self.data_filter):
                log.loading = False
                log.write(single_alert)
                self.loaded += 1
        except ValueError as ve:
            if hasattr(ve, 'message'):
                reason = ve.message
            elif hasattr(ve, 'reason'):
                reason = f"{ve}"
            else:
                reason = f"{ve}"
            tb = traceback.extract_stack()
            error_screen = ErrorScreen(
                trace=tb,
                reason=reason
            )
            await self.push_screen(error_screen)

    @work(exclusive=False, thread=True)
    async def on_mount(self):
        """
        Place elements on the screen, pump events
        :return:
        """
        log = self.query_one('#events', RichLog)
        await self.pump_events(log)
        self.notify(
            title="Finished loading events",
            severity="information" if self.loaded > 0 else "warning",
            timeout=15,
            message=f"Number of messages loaded: {self.loaded}"
        )
