from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Any, Callable

from rich.console import Console
from rich.live import Live

from rich.table import Table

from suricatalog.filter import BaseFilter, all_events_filter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO


class FlowApp:
    __CONSOLE = Console()

    @staticmethod
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
        with Live(alerts_tbl, refresh_per_second=10):
            afr = AggregatedFlowProtoReport()
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
        FlowApp.__CONSOLE.print(alerts_tbl)

    @staticmethod
    def print(*objects: Any):
        FlowApp.__CONSOLE.print(objects)

    @classmethod
    def host_data_use(
            cls,
            timestamp: datetime,
            eve_files: List[Path],
            row_filter: Callable,
            ip_address: any
    ):
        hdu = HostDataUseReport()
        for event in get_events_from_eve(
                timestamp=timestamp,
                eve_files=eve_files,
                row_filter=row_filter):
            hdu.ingest_data(event, ip_address)
        FlowApp.__CONSOLE.print(f"[b]Net-flow[/b]: {ip_address} = {hdu.bytes} bytes")

    @classmethod
    def get_agents(
            cls,
            timestamp: datetime,
            eve_files: List[Path],
            row_filter: Callable
    ):
        tua = TopUserAgents()
        for event in get_events_from_eve(
                timestamp=timestamp,
                eve_files=eve_files,
                row_filter=row_filter):
            tua.ingest_data(event)
        FlowApp.__CONSOLE.print(tua.agents)
