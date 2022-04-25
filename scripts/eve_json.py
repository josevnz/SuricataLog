#!/usr/bin/env python
"""
This script is inspired by the examples provided on
[15.1.3. Eve JSON ‘jq’ Examples](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html)

A few things:
* The output uses colorized JSON

"""

import argparse
from pathlib import Path
from ipaddress import ip_address

from rich.console import Console
from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, all_events_filter, AlwaysTrueFilter
from suricatalog.log import DEFAULT_EVE, get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO
from suricatalog.ui import EveLogApp, one_shot_flow_table

if __name__ == "__main__":
    CONSOLE = Console()
    PARSER = argparse.ArgumentParser(description=__doc__)
    EXCLUSIVE_FLAGS = PARSER.add_mutually_exclusive_group()
    EXCLUSIVE_FLAGS.add_argument(
        "--nxdomain",
        action='store_true',
        default=False,
        help=f"Show DNS records with NXDOMAIN"
    )
    EXCLUSIVE_FLAGS.add_argument(
        "--payload",
        action='store_true',
        default=False,
        help=f"Show alerts with a printable payload"
    )
    EXCLUSIVE_FLAGS.add_argument(
        "--flow",
        action='store_true',
        default=False,
        help=f"Aggregated flow report per protocol and destination port"
    )
    EXCLUSIVE_FLAGS.add_argument(
        "--netflow",
        type=ip_address,
        action='store',
        help=f"Get the netflow for a given IP address"
    )
    EXCLUSIVE_FLAGS.add_argument(
        "--useragent",
        action='store_true',
        default=False,
        help=f"Top user agent in HTTP traffic"
    )
    PARSER.add_argument(
        'eve',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()

    try:
        if OPTIONS.nxdomain:
            EveLogApp.run(
                timestamp=DEFAULT_TIMESTAMP_10Y_AGO,
                eve_files=OPTIONS.eve,
                out_format='json',
                console=CONSOLE,
                title="Suricata NXDOMAIN filter",
                data_filter=NXDomainFilter()
            )
        elif OPTIONS.payload:
            EveLogApp.run(
                timestamp=DEFAULT_TIMESTAMP_10Y_AGO,
                eve_files=OPTIONS.eve,
                out_format='json',
                console=CONSOLE,
                title="Suricata alerts with printable payload",
                data_filter=WithPrintablePayloadFilter()
            )
        elif OPTIONS.flow:
            flow_tbl = one_shot_flow_table(
                eve=OPTIONS.eve,
                data_filter=AlwaysTrueFilter(),
                console=CONSOLE
            )
            CONSOLE.print(flow_tbl)
        elif OPTIONS.netflow:
            ip_address = OPTIONS.netflow.exploded
            hdu = HostDataUseReport()
            for event in get_events_from_eve(
                    timestamp=DEFAULT_TIMESTAMP_10Y_AGO,
                    eve_files=OPTIONS.eve,
                    row_filter=all_events_filter):
                hdu.ingest_data(event, ip_address)
            CONSOLE.print(f"[b]Net-flow[/b]: {ip_address} = {hdu.bytes} bytes")
        elif OPTIONS.useragent:
            tua = TopUserAgents()
            for event in get_events_from_eve(
                    timestamp=DEFAULT_TIMESTAMP_10Y_AGO,
                    eve_files=OPTIONS.eve,
                    row_filter=all_events_filter):
                tua.ingest_data(event)
            # TODO: Finish!!!

    except KeyboardInterrupt:
        CONSOLE.print("[bold]Program interrupted...[/bold]")
