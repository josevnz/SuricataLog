"""
Top user application related code
"""
from pathlib import Path
from typing import Type, List

from textual import work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Header, RichLog, Footer

from suricatalog import BASEDIR
from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import TopUserAgents


class TopUserApp(App):
    """
    Show top users
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
            data_filter: BaseFilter = None,
            eve: List[Path] = None
    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        :param data_filter:
        :param eve:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.data_filter = data_filter
        self.eve_files = eve

    def action_quit_app(self) -> None:
        """
        Exit app
        :return:
        """
        self.exit("Exiting Top user now...")

    def compose(self) -> ComposeResult:
        """
        Component placement
        :return:
        """
        yield Header()
        pretty = RichLog(
            id="agent",
            highlight=True,
            auto_scroll=True
        )
        pretty.loading = True
        yield pretty
        yield Footer()

    @work(exclusive=False)
    async def on_mount(self) -> None:
        """
        Populate TUI components with data
        :return:
        """
        top_user_agents = TopUserAgents()
        log = self.query_one("#agent", RichLog)
        log.loading = False
        for event in get_events_from_eve(
                eve_files=self.eve_files,
                data_filter=self.data_filter):
            await top_user_agents.ingest_data(event)
        log.write(top_user_agents.agents)
