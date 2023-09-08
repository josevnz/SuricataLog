import locale
from pathlib import Path
from typing import Type, List, Any, Dict

from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Footer, ListView, Header, ListItem, Pretty, DataTable

from suricatalog.log import get_events_from_eve
from suricatalog.filter import BaseFilter

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent


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
    def __extract__from_alert__(alert: Dict[str, Any]) -> Dict[str, Any]:
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


class RawAlert(BaseAlert):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.is_brief = None

    def set_is_brief(self, is_brief: bool = True):
        self.is_brief = is_brief

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView()
        yield Footer()

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")

    def on_mount(self) -> None:
        list_view = self.query_one(ListView)
        for event in get_events_from_eve(
                data_filter=self.filter,
                eve_files=self.eve_files
        ):
            if not self.filter.accept(event):
                continue

            if self.is_brief:
                brief_data = BaseAlert.__extract__from_alert__(event)
                brief = {
                    "Timestamp": brief_data['timestamp'],
                    "Severity": brief_data['severity'],
                    "Signature": brief_data['signature'],
                    "Protocol": brief_data['protocol'],
                    "Destination": f"{brief_data['dest_ip']}:{brief_data['dest_port']}",
                    "Source": f"{brief_data['src_ip']}:{brief_data['src_port']}"
                }
                list_view.append(ListItem(Pretty(brief)))
            else:
                list_view.append(ListItem(Pretty(event)))


class TableAlert(BaseAlert):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        alerts_tbl = self.query_one(DataTable)
        alerts_tbl.add_column("Timestamp")
        alerts_tbl.add_column("Severity")
        alerts_tbl.add_column("Signature")
        alerts_tbl.add_column("Protocol")
        alerts_tbl.add_column("Destination")
        alerts_tbl.add_column("Source")
        alerts_tbl.add_column("Payload")
        alert_cnt = 0
        for event in get_events_from_eve(
                data_filter=self.filter,
                eve_files=self.eve_files
        ):
            if not self.filter.accept(event):
                continue
            brief_data = BaseAlert.__extract__from_alert__(event)
            alerts_tbl.add_row(
                brief_data['timestamp'],
                brief_data['severity'],
                brief_data['signature'],
                brief_data['protocol'],
                f"{brief_data['dest_ip']}:{brief_data['dest_port']}",
                f"{brief_data['src_ip']}:{brief_data['src_port']}",
                brief_data['payload_printable']
            )
            alert_cnt += 1

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")
