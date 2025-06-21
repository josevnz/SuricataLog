"""
Collection of mini apps, canned reports.
"""
import inspect
from pathlib import Path

import pyperclip
from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import DataTable, Footer, Header
from textual.worker import get_current_worker

from suricatalog.clipboard import copy_from_table
from suricatalog.filter import BaseFilter
from suricatalog.log import EveLogHandler
from suricatalog.report import AggregatedFlowProtoReport


class FlowApp(App):
    """
    Flow traffic application
    """
    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("y,c", "copy_table", "Copy to clipboard")
    ]
    ENABLE_COMMAND_PALETTE = False
    current_sorts: set = set()

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            data_filter: BaseFilter = None,
            eve: list[Path] = None
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

    def action_copy_table(self) -> None:
        """
        Copy contents to the clipboard
        :return:
        """
        table_data = self.query_one(DataTable)
        try:
            _, ln = copy_from_table(table_data)
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
        alerts_tbl = DataTable()
        alerts_tbl.show_header = True
        alerts_tbl.add_column("Protocol")
        alerts_tbl.add_column("Port")
        alerts_tbl.add_column("Count")
        alerts_tbl.zebra_stripes = True
        alerts_tbl.loading = True
        alerts_tbl.cursor_type = 'row'
        alerts_tbl.tooltip = inspect.cleandoc("""
        Network flow details
        """)
        yield alerts_tbl
        yield Footer()

    @work(exclusive=True, thread=True)
    async def update_flow_table(self, afr: AggregatedFlowProtoReport):
        alerts_tbl = self.query_one(DataTable)
        worker = get_current_worker()
        for (dest_ip_port, cnt) in afr.port_proto_count.items():
            if not worker.is_cancelled:
                self.call_from_thread(
                    alerts_tbl.add_row,
                    dest_ip_port[0],
                    str(dest_ip_port[1]),
                    str(cnt)
                )

    async def on_mount(self) -> None:
        """
        Populate components of the app on screen with relevant data
        :return:
        """
        alerts_tbl = self.query_one(DataTable)
        afr = AggregatedFlowProtoReport()
        eve_lh = EveLogHandler()
        cnt = 0
        for event in eve_lh.get_events(
                eve_files=self.eve,
                data_filter=self.data_filter):
            if not self.data_filter.accept(event):
                continue
            await afr.ingest_data(event)
            cnt += 1
        alerts_tbl.loading = False
        self.notify(
            message=f"Aggregated {cnt} events",
            title="Aggregated events",
            severity="information" if cnt > 0 else "error",
        )
        self.update_flow_table(afr=afr)

    def sort_reverse(self, sort_type: str):
        """
        Determine if `sort_type` is ascending or descending.
        :param sort_type: Keep track of column being sorted.
        """
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        """
        Handle clicks on table hear
        :param event:
        :return:
        """
        alerts_tbl: DataTable = event.data_table
        alerts_tbl.sort(
            event.column_key,
            reverse=self.sort_reverse(event.column_key.value)
        )
