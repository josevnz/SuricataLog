import locale
import textwrap
from pathlib import Path
from typing import Type, List, Any, Dict, Union

from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Pretty, DataTable, Button

from suricatalog.log import get_events_from_eve
from suricatalog.filter import BaseFilter

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent


class DetailScreen(ModalScreen):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = BASEDIR.joinpath('css').joinpath('details_screen.tcss')

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            data: str = None
    ):
        super().__init__(name, ident, classes)
        self.data = data

    def compose(self) -> ComposeResult:
        yield Pretty(self.data)
        button = Button("Close", variant="primary", id="close")
        button.tooltip = "Go back to main screen"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class BaseAlert(App):

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.eve_files = None
        self.filter = None

    @staticmethod
    def __get_key_from_map__(map1: Dict[str, Any], keys: List[str]):
        """
        Return the first matching key from a map
        :param map1:
        :param keys:
        :return: Nothing ig none of the keys are in the map
        """
        val = ""
        for key in keys:
            if key in map1:
                val = map1[key]
                break
        return val

    @staticmethod
    async def __extract__from_alert__(alert: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = alert['timestamp']
        dest_port = str(BaseAlert.__get_key_from_map__(alert, ['dest_port']))
        dest_ip = BaseAlert.__get_key_from_map__(alert, ['dest_ip'])
        src_ip = BaseAlert.__get_key_from_map__(alert, ['src_ip'])
        src_port = str(BaseAlert.__get_key_from_map__(alert, ['src_port']))
        protocol = BaseAlert.__get_key_from_map__(alert, ['app_proto', 'proto'])
        severity = alert['alert']['severity']
        signature = alert['alert']['signature'],
        payload_printable = alert['payload_printable'] if 'payload_printable' in alert else ""
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
        if not the_filter:
            raise ValueError("Filter is required")
        self.filter = the_filter

    def set_eve_files(self, eve_files: List[Path]):
        if not eve_files:
            raise ValueError("One or more eve files is required")
        self.eve_files = eve_files


class TableAlert(BaseAlert):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.events: Union[Dict[Dict[str, any]]] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        alerts_tbl = DataTable()
        alerts_tbl.show_header = True
        alerts_tbl.add_column("Timestamp")
        alerts_tbl.add_column("Severity")
        alerts_tbl.add_column("Signature")
        alerts_tbl.add_column("Protocol")
        alerts_tbl.add_column("Destination")
        alerts_tbl.add_column("Source")
        alerts_tbl.add_column("Payload")
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
        alerts_tbl = self.query_one(DataTable)
        alert_cnt = 0
        alerts_tbl.loading = False
        for event in get_events_from_eve(
                data_filter=self.filter,
                eve_files=self.eve_files
        ):
            if not self.filter.accept(event):
                continue
            brief_data = await BaseAlert.__extract__from_alert__(event)
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

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        alerts_tbl: DataTable = event.data_table
        if event.column_index < 2:
            alerts_tbl.sort(event.column_key)

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row_key = event.row_key
        row = table.get_row(row_key)
        data = self.events[row[0]]
        runner_detail = DetailScreen(data=data)
        self.push_screen(runner_detail)

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")
