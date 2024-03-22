import textwrap
import traceback
from pathlib import Path
from typing import Type, List

from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Header, DataTable, Footer, Digits, RichLog

from suricatalog import BASEDIR
from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.screens import ErrorScreen


class FlowApp(App):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            data_filter: BaseFilter = None,
            eve: List[Path] = None
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.data_filter = data_filter
        self.eve = eve

    def action_quit_app(self) -> None:
        self.exit("Exiting Net-Flow now...")

    def compose(self) -> ComposeResult:
        yield Header()
        alerts_tbl = DataTable()
        alerts_tbl.show_header = True
        alerts_tbl.add_column("Protocol")
        alerts_tbl.add_column("Port")
        alerts_tbl.add_column("Count")
        alerts_tbl.zebra_stripes = True
        alerts_tbl.loading = True
        alerts_tbl.cursor_type = 'row'
        alerts_tbl.tooltip = textwrap.dedent("""
        Network flow details
        """)
        yield alerts_tbl
        yield Footer()

    async def on_mount(self) -> None:
        alerts_tbl = self.query_one(DataTable)
        alert_cnt = 0
        afr = AggregatedFlowProtoReport()
        for event in get_events_from_eve(
                eve_files=self.eve,
                data_filter=self.data_filter):
            if not self.data_filter.accept(event):
                continue
            await afr.ingest_data(event)
        alerts_tbl.loading = False
        for (dest_ip_port, cnt) in afr.port_proto_count.items():
            alerts_tbl.add_row(
                dest_ip_port[0],
                str(dest_ip_port[1]),
                str(cnt)
            )
            alert_cnt += 1

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        alerts_tbl: DataTable = event.data_table
        alerts_tbl.sort(event.column_key)


class HostDataUse(App):
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
        super().__init__(driver_class, css_path, watch_css)
        self.ip_address = ip_address
        self.data_filter: BaseFilter = data_filter
        self.eve = eve

    def action_quit_app(self) -> None:
        self.exit("Exiting Net-Flow now...")

    def compose(self) -> ComposeResult:
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
        host_data_user_report = HostDataUseReport()
        for event in get_events_from_eve(
                eve_files=self.eve,
                data_filter=self.data_filter):
            await host_data_user_report.ingest_data(event, self.ip_address)
        digits = self.query_one('#netflow', Digits)
        digits.update(f"{host_data_user_report.bytes:n} bytes")
        digits.loading = False


class TopUserApp(App):
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
        super().__init__(driver_class, css_path, watch_css)
        self.data_filter = data_filter
        self.eve_files = eve

    def action_quit_app(self) -> None:
        self.exit("Exiting Top user now...")

    def compose(self) -> ComposeResult:
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
        top_user_agents = TopUserAgents()
        log = self.query_one("#agent", RichLog)
        log.loading = False
        for event in get_events_from_eve(
                eve_files=self.eve_files,
                data_filter=self.data_filter):
            await top_user_agents.ingest_data(event)
        log.write(top_user_agents.agents)


class OneShotApp(App):
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
        super().__init__(driver_class, css_path, watch_css)
        self.data_filter = data_filter
        self.eve = eve
        self.loaded = 0

    def action_quit_app(self) -> None:
        self.exit(f"Exiting {self.title} now...")

    def compose(self) -> ComposeResult:
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
        log = self.query_one('#events', RichLog)
        await self.pump_events(log)
        if self.loaded > 0:
            self.notify(
                title="Finished loading events",
                severity="information",
                timeout=5,
                message=f"Number of messages loaded: {self.loaded}"
            )
