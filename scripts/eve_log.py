#!/usr/bin/env python
"""
Show Suricata alerts
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
import json
from pathlib import Path

from rich.theme import Theme
from rich.traceback import install
from rich import pretty
from rich.console import Console
from suricatalog import DEFAULT_EVE, parse_timestamp, get_alerts_from_eve, DEFAULT_TIMESTAMP_10M_AGO
from suricatalog.ui import one_shot_alert_table

pretty.install()
install(show_locals=True)

FORMATS = ('json', 'table')

if __name__ == "__main__":
    CONSOLE = Console()
    PARSER = argparse.ArgumentParser(description=__doc__)
    PARSER.add_argument(
        "--timestamp",
        type=parse_timestamp,
        default=DEFAULT_TIMESTAMP_10M_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10M_AGO})"
    )
    PARSER.add_argument(
        "--formats",
        type=str,
        default=FORMATS[0],
        choices=FORMATS,
        help=f"Choose the output format ({' '.join(FORMATS)})"
    )
    PARSER.add_argument(
        'eve',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()
    try:
        if OPTIONS.formats == "json":
            for alert in get_alerts_from_eve(eve_files=OPTIONS.eve, timestamp=OPTIONS.timestamp):
                CONSOLE.print(json.dumps(alert, indent=6, sort_keys=True))
        elif OPTIONS.formats == "table":
            alerts_tbl = one_shot_alert_table(
                timestamp=OPTIONS.timestamp,
                eve=OPTIONS.eve,
                console=CONSOLE,
                alerts_retriever=get_alerts_from_eve
            )
            CONSOLE.print(alerts_tbl)
        else:
            raise NotImplementedError(f"I don't know how to handle {OPTIONS.format}!")
    except KeyboardInterrupt:
        CONSOLE.print("[bold]Program interrupted...[/bold]")
