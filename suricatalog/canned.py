from __future__ import annotations

from pathlib import Path
from typing import List, Callable, Any
import locale

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Digits, Pretty, DataTable

from suricatalog.filter import BaseFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.utility import load_css

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent


def get_one_shot_flow_table(
        *,
        eve: List[Path],
        data_filter: BaseFilter
) -> App:
    logs = ' '.join(map(lambda x: str(x), eve))

    class FlowApp(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]

        def action_quit_app(self) -> None:
            self.exit("Exiting Net-Flow now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield DataTable()
            yield Footer()

        def on_mount(self) -> None:
            alerts_tbl = self.query_one(DataTable)
            alerts_tbl.show_header = True
            alerts_tbl.add_column("Destination IP")
            alerts_tbl.add_column("Port")
            alerts_tbl.add_column("Count")
            alert_cnt = 0
            afr = AggregatedFlowProtoReport()
            for event in get_events_from_eve(
                    eve_files=eve,
                    data_filter=data_filter):
                if not data_filter.accept(event):
                    continue
                afr.ingest_data(event)
            for (dest_ip_port, cnt) in afr.port_proto_count.items():
                alerts_tbl.add_row(
                    dest_ip_port[0],
                    str(dest_ip_port[1]),
                    Text(str(cnt), style="italic #03AC13", justify="right")
                )
                alert_cnt += 1

    flow_app = FlowApp()
    flow_app.title = f"SuricataLog FLOW protocol, logs={logs}"
    return flow_app


def get_host_data_use(
        eve_files: List[Path],
        data_filter: BaseFilter,
        ip_address: any
) -> App:
    host_data_user_report = HostDataUseReport()
    for event in get_events_from_eve(
            eve_files=eve_files,
            data_filter=data_filter):
        host_data_user_report.ingest_data(event, ip_address)

    class HostDataUse(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]
        CSS_FILE = BASEDIR.joinpath('css').joinpath('canned.css')
        CSS = load_css(CSS_FILE)

        def action_quit_app(self) -> None:
            self.exit("Exiting Net-Flow now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield Digits(f"{host_data_user_report.bytes:n} bytes", id="netflow")
            yield Footer()

    hdu = HostDataUse()
    hdu.title = f"SuricataLog Net-Flow for: {ip_address}"
    return hdu


def get_agents(
        eve_files: List[Path],
        data_filter: BaseFilter
) -> App:
    top_user_agents = TopUserAgents()
    for event in get_events_from_eve(
            eve_files=eve_files,
            data_filter=data_filter):
        top_user_agents.ingest_data(event)

    class TopUserApp(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]
        CSS_FILE = BASEDIR.joinpath('css').joinpath('canned.css')
        CSS = load_css(CSS_FILE)

        def action_quit_app(self) -> None:
            self.exit("Exiting Top user now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield Pretty(top_user_agents.agents)
            yield Footer()

    top_user_app = TopUserApp()
    top_user_app.title = f"SuricataLog User Agents"
    return top_user_app


def get_capture(
        *,
        eve: List[Path],
        retriever: Callable = get_events_from_eve,
        data_filter: BaseFilter,
        title: str
) -> App:
    events: List[Any] = [single_alert for single_alert in retriever(eve_files=eve, data_filter=data_filter)]

    class OneShotApp(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]

        def action_quit_app(self) -> None:
            self.exit(f"Exiting {title} now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield Pretty(events)
            yield Footer()

    one_shot_app = OneShotApp()
    one_shot_app.title = f"{title}"
    return one_shot_app
