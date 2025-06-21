"""
Alert applications
"""
import inspect
import traceback
from pathlib import Path
from typing import Any

import pyperclip
from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.reactive import Reactive
from textual.widgets import DataTable, Footer, Header
from textual.worker import get_current_worker

from suricatalog.clipboard import copy_from_table
from suricatalog.filter import BaseFilter
from suricatalog.log import EveLogHandler
from suricatalog.providers import TableAlertProvider, TableColumns
from suricatalog.screens import DetailScreen, ErrorScreen


class BaseAlertApp(App):
    """
    Base application for alert applications, shared logic
    """

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.eve_files = None
        self.filter = None

    @staticmethod
    def __get_key_from_map__(data: dict[str, Any], keys: list[str]) -> str | None:
        """
        Return the first matching key from a map
        :param data:
        :param keys:
        :return: Nothing if none of the keys are in the map
        """
        val = ""
        for key in keys:
            if key in data:
                val = data[key]
                break
        return val

    @staticmethod
    async def extract_from_alert(alert: dict[str, Any]) -> dict[str, Any]:
        """
        Extract alerts from event
        :param alert:
        :return:
        """
        timestamp = alert.get('timestamp')
        if not timestamp:
            return {}
        dest_port = str(BaseAlertApp.__get_key_from_map__(data=alert, keys=['dest_port']))
        dest_ip = BaseAlertApp.__get_key_from_map__(data=alert, keys=['dest_ip'])
        src_ip = BaseAlertApp.__get_key_from_map__(data=alert, keys=['src_ip'])
        src_port = str(BaseAlertApp.__get_key_from_map__(data=alert, keys=['src_port']))
        protocol = BaseAlertApp.__get_key_from_map__(data=alert, keys=['app_proto', 'proto'])
        severity = alert['alert']['severity']
        if 'signature' in alert:
            signature = alert.get('signature', '')
        else:
            signature = alert['alert'].get('signature', '')
        payload_printable = alert.get('payload_printable', '')
        return {
            "timestamp": timestamp,
            "dest_port": dest_port,
            "src_ip": src_ip,
            "dest_ip": dest_ip,
            "src_port": src_port,
            "protocol": protocol,
            "severity": severity,
            "signature": signature,
            "payload_printable": payload_printable
        }

    def set_filter(self, the_filter: BaseFilter):
        """
        Set filter for application
        :param the_filter:
        :return:
        """
        if not the_filter:
            raise ValueError("Filter is required")
        self.filter = the_filter

    def set_eve_files(self, eve_files: list[Path]):
        """
        Set eve files for application
        :param eve_files:
        :return:
        """
        if not eve_files:
            raise ValueError("One or more eve files is required")
        self.eve_files = eve_files


class TableAlertApp(BaseAlertApp):
    """
    Concrete implementation for alert application
    """
    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("c", "copy_table", "Copy to clipboard")
    ]
    ENABLE_COMMAND_PALETTE = True
    COMMANDS = App.COMMANDS | {TableAlertProvider}
    current_sorts: set = set()
    enable_developer_warnings: Reactive[bool] = Reactive(False)

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.events: dict[dict[str, any]] | dict = {}

    async def show_error(
            self,
            trace: traceback.StackSummary | None,
            reason: str | None
    ) -> None:
        """
        Show error on special screen
        :param trace:
        :param reason:
        :return:
        """
        error_src = ErrorScreen(trace=trace, reason=reason)
        await self.push_screen(error_src)

    def compose(self) -> ComposeResult:
        """
        Place TUI components
        :return:
        """
        yield Header()
        alerts_tbl = DataTable()
        alerts_tbl.show_header = True
        alerts_tbl.add_column(TableColumns.TIMESTAMP.name)
        alerts_tbl.add_column(TableColumns.SEVERITY.name)
        alerts_tbl.add_column(TableColumns.SIGNATURE.name)
        alerts_tbl.add_column(TableColumns.PROTOCOL.name)
        alerts_tbl.add_column(TableColumns.DESTINATION.name)
        alerts_tbl.add_column(TableColumns.SOURCE.name)
        alerts_tbl.add_column(TableColumns.PAYLOAD.name)
        alerts_tbl.zebra_stripes = True
        alerts_tbl.loading = True
        alerts_tbl.cursor_type = 'row'
        alerts_tbl.tooltip = inspect.cleandoc("""
        Suricata alert details. Select a row to get full details.
        """)
        yield alerts_tbl
        yield Footer()

    @work(exclusive=True, thread=True)
    async def update_alert_table(self):
        alerts_tbl = self.query_one(DataTable)
        alert_cnt = 0
        eve_lh = EveLogHandler()
        worker = get_current_worker()

        for event in eve_lh.get_events(data_filter=self.filter, eve_files=self.eve_files):
            self.log.debug(f"Got event (filter={self.filter}): {event}")
            if not self.filter.accept(event):
                continue
            brief_data = await BaseAlertApp.extract_from_alert(event)
            if not brief_data:
                self.log.warning("Skipping malformed event: %s", event)
            timestamp = brief_data['timestamp']
            if not worker.is_cancelled:
                self.call_from_thread(
                    alerts_tbl.add_row,
                    timestamp,
                    brief_data['severity'],
                    brief_data['signature'],
                    brief_data['protocol'],
                    f"{brief_data['dest_ip']}:{brief_data['dest_port']}",
                    f"{brief_data['src_ip']}:{brief_data['src_port']}",
                    brief_data['payload_printable']
                )
            alert_cnt += 1
            self.events[timestamp] = event
        alerts_tbl.sub_title = f"Total alerts: {alert_cnt}"
        if not worker.is_cancelled:
            self.call_from_thread(
                self.notify,
                title="Finish loading events",
                timeout=5,
                severity="information" if alert_cnt > 0 else "error",
                message=inspect.cleandoc(f"""
                        Loaded {alert_cnt} messages.
                        Click on a row to get more details, CTR+\\ to search
                        """) if alert_cnt > 0 else "Nothing to display."
            )

        if not alert_cnt:
            val = self.call_from_thread(
                self.show_error,
                reason="Could not recover a single alert.",
                trace=None
            )
            if val:
                await val

    async def on_mount(self) -> None:
        """
        Initialize TUI components
        :return:
        """
        alerts_tbl = self.query_one(DataTable)
        alerts_tbl.loading = False
        try:
            self.update_alert_table()
        except ValueError as ve:
            if hasattr(ve, 'reason'):
                reason = f"{ve}"
            elif hasattr(ve, 'message'):
                reason = ve.message
            else:
                reason = f"{ve}"
            self.log.error(f"Fatal error: {reason}")
            tb = traceback.extract_stack()
            self.log.error(tb)
            await self.show_error(trace=tb, reason=str(ve))

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
        Handle click events on table
        :param event:
        :return:
        """
        alerts_tbl: DataTable = event.data_table
        alerts_tbl.sort(
            event.column_key,
            reverse=self.sort_reverse(event.column_key.value)
        )

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        """
        Handle click on rows
        :param event:
        :return:
        """
        table = event.data_table
        row_key = event.row_key
        row = table.get_row(row_key)
        data = self.events[row[0]]
        runner_detail = DetailScreen(data=data)
        self.push_screen(runner_detail)

    def action_quit_app(self) -> None:
        """
        Handle exit action
        :return:
        """
        self.exit("Exiting Alerts now...")

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
