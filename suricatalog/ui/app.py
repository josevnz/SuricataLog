import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Any, Callable, Dict

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.status import Status
from rich.table import Table
from textual import events
from textual.app import App
from textual.widgets import ScrollView
from rich.traceback import install
from rich import pretty

from suricatalog.filter import BaseFilter, all_events_filter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO
from suricatalog.ui.widgets import EvelogAppHeader, EvelogAppFooter, SURICATALOG_HEADER_FOOTER_STYLE

pretty.install()
install(show_locals=True)


class EveLogApp(App):
    __CONSOLE = Console()

    @staticmethod
    def __get_key_from_map__(map1: Dict[str, Any], key: str):
        return map1[key] if key in map1 else ""

    def __init__(
            self,
            *args,
            timestamp: datetime,
            eve_files: List[Path],
            out_format: str,
            data_filter: BaseFilter,
            debug: bool = False,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.body = None
        self.timestamp = timestamp
        self.eve_files = eve_files
        self.out_format = out_format
        self.data_filter = data_filter
        self.debug = debug

    @staticmethod
    def print(*objects: Any):
        EveLogApp.__CONSOLE.print(objects)

    @staticmethod
    def one_shot_alert_table(
            *,
            eve: List[Path],
            timestamp: datetime,
            alerts_retriever: Callable,
            console: Console,
            data_filter: BaseFilter
    ) -> Table:
        """
        Read and parse all the alerts from the eve.json file. It may use lots of memory and take a while to render...
        :param data_filter:
        :param eve:
        :param timestamp:
        :param alerts_retriever:
        :param console:
        :return:
        """
        alerts_tbl = Table(show_header=False)
        alerts_tbl.add_column("Timestamp", style="dim", no_wrap=True)
        alerts_tbl.add_column("Severity")
        alerts_tbl.add_column("Signature", style="Blue")
        alerts_tbl.add_column("Protocol", justify="right")
        alerts_tbl.add_column("Destination", justify="right")
        alerts_tbl.add_column("Source", justify="right")
        alerts_tbl.add_column("Payload", justify="left", no_wrap=False)
        alert_cnt = 0
        for alert in alerts_retriever(eve_files=eve, timestamp=timestamp):
            if not data_filter.accept(alert):
                continue
            try:
                dest_ip = EveLogApp.__get_key_from_map__(alert, 'dest_ip')
                dest_port = str(EveLogApp.__get_key_from_map__(alert, 'dest_port'))
                src_ip = EveLogApp.__get_key_from_map__(alert, 'src_ip')
                src_port = str(alert['src_port']) if 'src_port' in alert else ""
                alrt_int = alert['alert']['severity']
                severity = f"[yellow]{str(alrt_int)}[/yellow]" \
                    if alrt_int <= 5 else f"[yellow]{str(alrt_int)}[/yellow]"
                alerts_tbl.add_row(
                    alert['timestamp'],
                    severity,
                    alert['alert']['signature'],
                    f"[red]{alert['app_proto']}[/red]",
                    f"[green]{dest_ip}[/green]:[bold]{dest_port}[/bold]",
                    f"[yellow]{src_ip}[/yellow]:[bold]{src_port}[/bold]",
                    alert['payload_printable']
                )
                alert_cnt += 1
            except KeyError:
                console.print(alert['alert'])
                raise
        return alerts_tbl

    @staticmethod
    def one_shot_json(
            *,
            eve: List[Path],
            timestamp: datetime,
            alerts_retriever: Callable,
            data_filter: BaseFilter
    ) -> str:
        alerts: List[str] = [
            json.dumps(single_alert, indent=2, sort_keys=True) for single_alert in
            alerts_retriever(eve_files=eve, timestamp=timestamp) if data_filter.accept(single_alert)
        ]
        return "\n".join(alerts)

    @staticmethod
    def one_shot_brief(
            *,
            eve: List[Path],
            timestamp: datetime,
            alerts_retriever: Callable,
            data_filter: BaseFilter
    ) -> Table:
        grid = Table.grid()
        for single_alert in alerts_retriever(eve_files=eve, timestamp=timestamp):
            if not data_filter.accept(single_alert):
                continue
            dest_port = str(EveLogApp.__get_key_from_map__(single_alert, 'dest_port'))
            src_ip = EveLogApp.__get_key_from_map__(single_alert, 'src_ip')
            dest_ip = EveLogApp.__get_key_from_map__(single_alert, 'dest_ip')
            src_port = EveLogApp.__get_key_from_map__(single_alert, 'src_port')
            alrt_int = single_alert['alert']['severity']
            severity = f"[yellow]{str(alrt_int)}[/yellow]" if alrt_int <= 5 else f"[yellow]{str(alrt_int)}[/yellow]"
            grid.add_row(
                Panel(
                    textwrap.dedent(f"""
    [b]Timestamp:[/b] {single_alert['timestamp']}
    [b]Severity:[/b] {severity}
    [b]Signature:[/b] {single_alert['alert']['signature']}
    [b]Protocol:[/b] [red]{single_alert['app_proto']}[/red]
    [b]Destination:[/b] [green]{dest_ip}[/green]:[bold]{dest_port}[/bold] 
    [b]Source:[/b] [yellow]{src_ip}[/yellow]:[bold]{src_port}[/bold]"""
                                    ),
                    expand=False
                )
            )
        return grid

    async def on_load(self, event: events.Load) -> None:
        if self.debug:
            self.console.print(event)
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        if self.debug:
            self.console.print(event)
        self.body = body = ScrollView(auto_width=True)
        header = EvelogAppHeader()
        header.style = SURICATALOG_HEADER_FOOTER_STYLE
        footer = EvelogAppFooter()
        await self.view.dock(header, edge="top")
        await self.view.dock(footer, edge="bottom")
        await self.view.dock(body)

        async def add_content():

            if self.out_format == "table":
                tbl = EveLogApp.one_shot_alert_table(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    console=self.console,
                    alerts_retriever=get_events_from_eve,
                    data_filter=self.data_filter
                )
                await body.update(tbl)
            elif self.out_format == "json":
                json_lines = EveLogApp.one_shot_json(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    alerts_retriever=get_events_from_eve,
                    data_filter=self.data_filter
                )
                await body.update(json_lines)
            elif self.out_format == "brief":
                columns = EveLogApp.one_shot_brief(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    alerts_retriever=get_events_from_eve,
                    data_filter=self.data_filter
                )
                await body.update(columns)
            else:
                raise NotImplementedError(f"I don't know how to handle {self.out_format}!")

        with Status(f"Parsing {self.eve_files}", console=EveLogApp.__CONSOLE) as status:
            status.start()
            await self.call_later(add_content)
            status.stop()


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
            eve_files: list[Path],
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
            eve_files: list[Path],
            row_filter: Callable
    ):
        tua = TopUserAgents()
        for event in get_events_from_eve(
                timestamp=timestamp,
                eve_files=eve_files,
                row_filter=row_filter):
            tua.ingest_data(event)
        FlowApp.__CONSOLE.print(tua.agents)
