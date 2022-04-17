from pathlib import Path
from datetime import datetime
from typing import Callable, List

from rich.console import Console
from rich.table import Table
from rich.progress import Progress


def one_shot_alert_table(
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
    alerts_tbl.add_column("Timestamp", style="dim")
    alerts_tbl.add_column("Severity")
    alerts_tbl.add_column("Signature", style="Blue")
    alerts_tbl.add_column("Protocol", justify="right")
    alerts_tbl.add_column("Destination", justify="right")
    alerts_tbl.add_column("Source", justify="right")
    alerts_tbl.add_column("Payload", justify="right")
    alert_cnt = 0
    with Progress(console=console, transient=False) as progress:
        task = progress.add_task(f"Parsing {logs}", total=100)
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
