#!/usr/bin/env python
"""
This script is inspired by the examples provided on
[15.1.3. Eve JSON ‘jq’ Examples](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html)

A few things:
* The output uses colorized/ scrollable JSON
* You can filter by timestamp

"""

import argparse
from pathlib import Path
from ipaddress import ip_address

from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, all_events_filter, AlwaysTrueFilter
from suricatalog.log import DEFAULT_EVE
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO, parse_timestamp
from suricatalog.ui.app import EveApp, one_shot_flow_table, host_data_use, get_agents

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description=__doc__)
    PARSER.add_argument(
        "--timestamp",
        type=parse_timestamp,
        default=DEFAULT_TIMESTAMP_10Y_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10Y_AGO})"
    )
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
        eve_app = EveApp()
        if OPTIONS.nxdomain:
            eve_app.title = "DNS records with NXDOMAIN"
        elif OPTIONS.payload:
            eve_app.title = "Inspect Alert Data (payload)"
        elif OPTIONS.flow:
            one_shot_flow_table(
                eve=OPTIONS.eve,
                data_filter=AlwaysTrueFilter()
            )
        elif OPTIONS.netflow:
            eve_app = host_data_use(
                timestamp=OPTIONS.timestamp,
                eve_files=OPTIONS.eve,
                row_filter=all_events_filter,
                ip_address=OPTIONS.netflow.exploded
            )
        elif OPTIONS.useragent:
            eve_app = get_agents(
                timestamp=OPTIONS.timestamp,
                eve_files=OPTIONS.eve,
                row_filter=all_events_filter
            )
        eve_app.compose()
        eve_app.run()
    except KeyboardInterrupt:
        pass
