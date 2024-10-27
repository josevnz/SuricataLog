"""
Host data use application
"""
import textwrap
from pathlib import Path
from typing import Type, List

from textual import work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Header, Digits, Footer

from suricatalog import BASEDIR
from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import HostDataUseReport


class HostDataUse(App):
    """
    Host data usage application
    """
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    CSS_PATH = BASEDIR.joinpath('css').joinpath('canned.tcss')
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            ip_address: str = None,
            data_filter: BaseFilter = None,
            eve: List[Path] = None

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

    def compose(self) -> ComposeResult:
        """
        Place components of the app on screen
        :return:
        """
        yield Header()
        digits = Digits(id="netflow")
        digits.loading = True
        digits.tooltip = textwrap.dedent("""
            Net FLow in bytes.
            """)
        yield digits
        yield Footer()

    @work(exclusive=False)
    async def on_mount(self) -> None:
        """
        Initialize TUI components with data
        :return:
        """
        host_data_user_report = HostDataUseReport()
        for event in get_events_from_eve(
                eve_files=self.eve,
                data_filter=self.data_filter):
            await host_data_user_report.ingest_data(event, self.ip_address)
        digits = self.query_one('#netflow', Digits)
        digits.update(f"{host_data_user_report.bytes:n} bytes")
        digits.loading = False
