import locale
from pathlib import Path
from typing import Type, List, Any, Dict

from textual.app import App, ComposeResult, CSSPathType
from textual.driver import Driver
from textual.widgets import Footer, ListView, Header, ListItem, Pretty

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
        val = ""
        for key in keys:
            if key in map1:
                val = map1[key]
                break
        return val


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

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")


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
                dest_port = str(BaseAlert.__get_key_from_map__(event, ['dest_port']))
                src_ip = BaseAlert.__get_key_from_map__(event, ['src_ip'])
                dest_ip = BaseAlert.__get_key_from_map__(event, ['dest_ip'])
                src_port = BaseAlert.__get_key_from_map__(event, ['src_port'])
                protocol = BaseAlert.__get_key_from_map__(event, ['app_proto', 'proto'])
                severity = event['alert']['severity']
                brief = {
                    "Timestamp": f"{event['timestamp']}",
                    "Severity": f"{severity}",
                    "Signature": f"{event['alert']['signature']}",
                    "Protocol": protocol,
                    "Destination": f"{dest_ip}:{dest_port}",
                    "Source": f"{src_ip}:{src_port}"
                }
                list_view.append(ListItem(Pretty(brief)))
            else:
                list_view.append(ListItem(Pretty(event)))
