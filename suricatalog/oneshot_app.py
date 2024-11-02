"""
One shot application related code
"""
import traceback
from pathlib import Path
from typing import Type, List

from textual import work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Header, RichLog, Footer

from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.screens import ErrorScreen


class OneShotApp(App):
    """
    One shot application, displays data based on filter
    """
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            eve: List[Path] = None,
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
            for single_alert in get_events_from_eve(eve_files=self.eve, data_filter=self.data_filter):
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

    @work(exclusive=False)
    async def on_mount(self):
        """
        Place elements on the screen
        :return:
        """
        log = self.query_one('#events', RichLog)
        await self.pump_events(log)
        if self.loaded > 0:
            self.notify(
                title="Finished loading events",
                severity="information",
                timeout=5,
                message=f"Number of messages loaded: {self.loaded}"
            )
