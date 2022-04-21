import json
import textwrap
from pathlib import Path
from datetime import datetime
from typing import Callable, List

from rich.columns import Columns
from rich.panel import Panel
from rich.traceback import install
from rich import pretty
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from textual import events
from textual.app import App
from textual.widgets import ScrollView

from suricatalog.log import get_alerts_from_eve

pretty.install()
install(show_locals=True)


def one_shot_alert_table(
        *,
        eve: List[Path],
        timestamp: datetime,
        alerts_retriever: Callable,
        console: Console
) -> Table:
    """
    Read and parse all the alerts from the eve.json file. It may use lots of memory and take a while to render...
    :param eve:
    :param timestamp:
    :param alerts_retriever:
    :param console:
    :return:
    """
    logs = ' '.join(map(lambda x: str(x), eve))
    alerts_tbl = Table(
        show_header=True,
        header_style="bold magenta",
        title=f"Suricata alerts for {timestamp}, logs={logs}",
        highlight=True
    )
    alerts_tbl.add_column("Timestamp", style="dim", no_wrap=True)
    alerts_tbl.add_column("Severity")
    alerts_tbl.add_column("Signature", style="Blue")
    alerts_tbl.add_column("Protocol", justify="right")
    alerts_tbl.add_column("Destination", justify="right")
    alerts_tbl.add_column("Source", justify="right")
    alerts_tbl.add_column("Payload", justify="right", no_wrap=False)
    alert_cnt = 0
    with Progress(console=console, transient=False) as progress:
        task = progress.add_task(f"Parsing {logs}", total=100)
        progress.update(task_id=task, completed=1.0)
        for alert in alerts_retriever(eve_files=eve, timestamp=timestamp):
            try:
                dest_ip = alert['dest_ip'] if 'dest_ip' in alert else ""
                dest_port = str(alert['dest_port']) if 'dest_port' in alert else ""
                src_ip = alert['src_ip'] if 'src_ip' in alert else ""
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
        progress.update(task_id=task, completed=100.0)
    alerts_tbl.show_footer
    return alerts_tbl


def one_shot_json(
        *,
        eve: List[Path],
        timestamp: datetime,
        alerts_retriever: Callable,
        console: Console
) -> str:
    with Progress(console=console, transient=False) as progress:
        task = progress.add_task(f"Parsing {eve}", total=100)
        progress.update(task_id=task, completed=1.0)
        alerts: List[str] = [
            json.dumps(single_alert, indent=2, sort_keys=True) for single_alert in alerts_retriever(
                eve_files=eve, timestamp=timestamp)
        ]
        progress.update(task_id=task, completed=100.0)
    return "\n".join(alerts)


def one_shot_brief(
        *,
        eve: List[Path],
        timestamp: datetime,
        alerts_retriever: Callable,
        console: Console
) -> Columns:
    with Progress(console=console, transient=False) as progress:
        task = progress.add_task(f"Parsing {eve}", total=100)
        progress.update(task_id=task, completed=1.0)
        alerts: List[Panel] = []
        for single_alert in alerts_retriever(eve_files=eve, timestamp=timestamp):
            dest_ip = single_alert['dest_ip'] if 'dest_ip' in single_alert else ""
            dest_port = str(single_alert['dest_port']) if 'dest_port' in single_alert else ""
            src_ip = single_alert['src_ip'] if 'src_ip' in single_alert else ""
            src_port = str(single_alert['src_port']) if 'src_port' in single_alert else ""
            alrt_int = single_alert['alert']['severity']
            severity = f"[yellow]{str(alrt_int)}[/yellow]" if alrt_int <= 5 else f"[yellow]{str(alrt_int)}[/yellow]"
            alerts.append(
                Panel(
                    textwrap.dedent(
                        f"""{single_alert['timestamp']}
{severity}
{single_alert['alert']['signature']}
[red]{single_alert['app_proto']}[/red]
[green]{dest_ip}[/green]:[bold]{dest_port}[/bold] 
[yellow]{src_ip}[/yellow]:[bold]{src_port}[/bold]"""
                    ),
                    expand=False
                )
            )
        progress.update(task_id=task, completed=100.0)
    return Columns(alerts, expand=False, equal=False, column_first=True)


class EveLogApp(App):

    def __init__(
            self,
            *args,
            timestamp: datetime,
            eve_files: List[Path],
            out_format: str,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.body = None
        self.timestamp = timestamp
        self.eve_files = eve_files
        self.out_format = out_format

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:

        self.body = body = ScrollView(auto_width=True)

        await self.view.dock(body)

        async def add_content():
            if self.out_format == "table":
                tbl = one_shot_alert_table(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    console=self.console,
                    alerts_retriever=get_alerts_from_eve
                )
                await body.update(tbl)
            elif self.out_format == "json":
                panels = one_shot_json(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    console=self.console,
                    alerts_retriever=get_alerts_from_eve
                )
                await body.update(panels)
            elif self.out_format == "brief":
                columns = one_shot_brief(
                    timestamp=self.timestamp,
                    eve=self.eve_files,
                    console=self.console,
                    alerts_retriever=get_alerts_from_eve
                )
                await body.update(columns)
            else:
                raise NotImplementedError(f"I don't know how to handle {self.out_format}!")

        await self.call_later(add_content)
