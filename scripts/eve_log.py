#!/usr/bin/env python
"""
Show Suricata alerts in different formats
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
from pathlib import Path

from rich.console import Console
from suricatalog.time import parse_timestamp, DEFAULT_TIMESTAMP_10M_AGO
from suricatalog.log import DEFAULT_EVE
from suricatalog.ui import EveLogApp
from suricatalog.filter import OnlyAlertsFilter

FORMATS = ('json', 'table', 'brief')

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
        EveLogApp.run(
            timestamp=OPTIONS.timestamp,
            eve_files=OPTIONS.eve,
            out_format=OPTIONS.formats,
            console=CONSOLE,
            title="Suricata alerts",
            data_filter=OnlyAlertsFilter()
        )
    except KeyboardInterrupt:
        CONSOLE.print("[bold]Program interrupted...[/bold]")
