from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Callable
import locale

from rich.live import Live

from rich.table import Table
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, LoadingIndicator, Digits, Pretty

from suricatalog.filter import BaseFilter, all_events_filter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent


def load_css(the_file: Path):
    with open(the_file, 'r') as css_data:
        return "\n".join(css_data.readlines())


def one_shot_flow_table(
        *,
        eve: List[Path],
        data_filter: BaseFilter
):
    """
    Read and parse all the alerts from the eve.json file. It may use lots of memory and take a while to render...
    :param data_filter:
    :param eve:
    :return:
    """
    logs = ' '.join(map(lambda x: str(x), eve))
    alerts_tbl = Table(
        show_header=True,
        header_style="bold magenta",
        title=f"Suricata FLOW protocol, logs={logs}",
        highlight=True
    )
    alerts_tbl.add_column("Destination IP")
    alerts_tbl.add_column("Port")
    alerts_tbl.add_column("Count", style="Blue")
    alert_cnt = 0
    afr = AggregatedFlowProtoReport()
    with Live(alerts_tbl, refresh_per_second=10) as live:
        for event in get_events_from_eve(
                eve_files=eve,
                timestamp=DEFAULT_TIMESTAMP_10Y_AGO,
                row_filter=all_events_filter):
            if not data_filter.accept(event):
                continue
            afr.ingest_data(event)
        for (dest_ip_port, cnt) in afr.port_proto_count.items():
            alerts_tbl.add_row(
                dest_ip_port[0],
                str(dest_ip_port[1]),
                str(cnt)
            )
            alert_cnt += 1
        live.console.clear_live()
        live.console.print(alerts_tbl)


def host_data_use(
        timestamp: datetime,
        eve_files: List[Path],
        row_filter: Callable,
        ip_address: any
) -> App:
    hdur = HostDataUseReport()
    for event in get_events_from_eve(
            timestamp=timestamp,
            eve_files=eve_files,
            row_filter=row_filter):
        hdur.ingest_data(event, ip_address)

    class HostDataUse(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]
        CSS_FILE = BASEDIR.joinpath('css').joinpath('one_shot_apps.css')
        CSS = load_css(CSS_FILE)

        def action_quit_app(self) -> None:
            self.exit("Exiting Net-Flow now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield Digits(f"{hdur.bytes:n} bytes", id="netflow")
            yield Footer()

    hdu = HostDataUse()
    hdu.title = f"Net-Flow for: {ip_address}"
    return hdu


def get_agents(
        timestamp: datetime,
        eve_files: List[Path],
        row_filter: Callable
) -> App:
    top_user_agents = TopUserAgents()
    for event in get_events_from_eve(
            timestamp=timestamp,
            eve_files=eve_files,
            row_filter=row_filter):
        top_user_agents.ingest_data(event)

    class TopUserApp(App):
        BINDINGS = [
            ("q", "quit_app", "Quit")
        ]
        CSS_FILE = BASEDIR.joinpath('css').joinpath('one_shot_apps.css')
        CSS = load_css(CSS_FILE)

        def action_quit_app(self) -> None:
            self.exit("Exiting Net-Flow now...")

        def compose(self) -> ComposeResult:
            yield Header()
            yield Pretty(top_user_agents.agents)
            yield Footer()

    top_user_app = TopUserApp()
    top_user_app.title = f"User Agents"
    return top_user_app


class EveApp(App):
    """Display multiple aspects of the eve.json log"""

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator()
        yield Footer()

    def action_quit(self) -> None:
        sys.exit(0)
