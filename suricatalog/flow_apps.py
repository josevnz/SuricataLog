"""
Collection of mini apps, canned reports.
"""
import textwrap
from pathlib import Path
from typing import Type, List

from textual import on
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Header, DataTable, Footer

from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport


class FlowApp(App):
    """
    Flow traffic application
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
        self.eve = eve

    def action_quit_app(self) -> None:
        """
        Exit the application
        :return:
        """
        self.exit("Exiting Net-Flow now...")

    def compose(self) -> ComposeResult:
        """
        Place components of the app on screen
        :return:
        """
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
        """
        Populate components of the app on screen with relevant data
        :return:
        """
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
        """
        Handle clicks on table hear
        :param event:
        :return:
        """
        alerts_tbl: DataTable = event.data_table
        alerts_tbl.sort(event.column_key)
