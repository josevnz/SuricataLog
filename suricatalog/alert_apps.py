"""
Alert applications
"""
import textwrap
import traceback
from pathlib import Path
from typing import Type, List, Any, Dict, Union

from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Footer, Header, DataTable

from suricatalog.log import get_events_from_eve
from suricatalog.filter import BaseFilter
from suricatalog.providers import TableAlertProvider, TableColumns
from suricatalog.screens import DetailScreen, ErrorScreen


class BaseAlertApp(App):
    """
    Base application for alert applications, shared logic
    """

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
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
    def __get_key_from_map__(map1: Dict[str, Any], keys: List[str]):
        """
        Return the first matching key from a map
        :param map1:
        :param keys:
        :return: Nothing if none of the keys are in the map
        """
        val = ""
        for key in keys:
            if key in map1:
                val = map1[key]
                break
        return val

    @staticmethod
    async def extract_from_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract alerts from event
        :param alert:
        :return:
        """
        timestamp = alert['timestamp']
        dest_port = str(BaseAlertApp.__get_key_from_map__(alert, ['dest_port']))
        dest_ip = BaseAlertApp.__get_key_from_map__(alert, ['dest_ip'])
        src_ip = BaseAlertApp.__get_key_from_map__(alert, ['src_ip'])
        src_port = str(BaseAlertApp.__get_key_from_map__(alert, ['src_port']))
        protocol = BaseAlertApp.__get_key_from_map__(alert, ['app_proto', 'proto'])
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

    def set_eve_files(self, eve_files: List[Path]):
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
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = True
    COMMANDS = App.COMMANDS | {TableAlertProvider}

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
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
        self.events: Union[Dict[Dict[str, any]], Dict] = {}

    async def show_error(
            self,
            trace: Union[traceback.StackSummary, None],
            reason: Union[str, None]
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
        alerts_tbl.tooltip = textwrap.dedent("""
        Suricata alert details. Select a row to get full details.
        """)
        yield alerts_tbl
        yield Footer()

    @work(exclusive=False)
    async def on_mount(self) -> None:
        """
        Initialize TUI components
        :return:
        """
        alerts_tbl = self.query_one(DataTable)
        alert_cnt = 0
        try:
            events = get_events_from_eve(
                    data_filter=self.filter,
                    eve_files=self.eve_files
            )
            for event in events:
                if not self.filter.accept(event):
                    continue
                brief_data = await BaseAlertApp.extract_from_alert(event)
                timestamp = brief_data['timestamp']
                alerts_tbl.add_row(
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
            self.notify(
                title="Finish loading events",
                timeout=5,
                severity="information",
                message=textwrap.dedent(f"""
                Loaded {alert_cnt} messages.
                Click on a row to get more details, CTR+\\ to search
                """)
            )
            if alert_cnt:
                alerts_tbl.loading = False
            else:
                await self.show_error(reason=None, trace=None)
        except ValueError as ve:
            if hasattr(ve, 'reason'):
                reason = f"{ve}"
            elif hasattr(ve, 'message'):
                reason = ve.message
            else:
                reason = f"{ve}"
            self.log.info(f"Fatal error: {reason}")
            tb = traceback.extract_stack()
            self.log.info(tb)
            await self.show_error(trace=tb, reason=str(ve))

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        """
        Handle click events on table
        :param event:
        :return:
        """
        alerts_tbl: DataTable = event.data_table
        alerts_tbl.sort(event.column_key)

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
