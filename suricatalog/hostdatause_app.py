"""
Host data use application
"""
import inspect
from pathlib import Path

import pyperclip
from textual import work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Digits, Footer, Header

from suricatalog import BASEDIR
from suricatalog.clipboard import copy_from_digits
from suricatalog.filter import BaseFilter
from suricatalog.log import EveLogHandler
from suricatalog.report import HostDataUseReport


class HostDataUse(App):
    """
    Host data usage application
    """
    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("y,c", "copy_digits", "Copy to clipboard")
    ]
    CSS_PATH = BASEDIR.joinpath('css').joinpath('canned.tcss')
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            ip_address: str = None,
            data_filter: BaseFilter = None,
            eve: list[Path] = None

    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        :param ip_address:
        :param data_filter:
        :param eve:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.ip_address = ip_address
        self.data_filter: BaseFilter = data_filter
        self.eve = eve

    def action_quit_app(self) -> None:
        """
        Quit application
        :return:
        """
        self.exit("Exiting Net-Flow now...")

    def action_copy_digits(self) -> None:
        """
        Copy contents to the clipboard
        :return:
        """
        digits = self.query_one(Digits)
        try:
            _, ln = copy_from_digits(digits)
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
        digits = Digits(id="netflow")
        digits.loading = True
        digits.tooltip = inspect.cleandoc("""
            Net FLow in bytes.
            """)
        yield digits
        yield Footer()

    @work(exclusive=True, thread=True)
    async def on_mount(self) -> None:
        """
        Initialize TUI components with data
        :return:
        """
        host_data_user_report = HostDataUseReport()
        eve_lh = EveLogHandler()
        for event in eve_lh.get_events(
                eve_files=self.eve,
                data_filter=self.data_filter):
            await host_data_user_report.ingest_data(event, self.ip_address)
        digits = self.query_one('#netflow', Digits)
        digits.update(f"{host_data_user_report.bytes:n} bytes")
        digits.loading = False
