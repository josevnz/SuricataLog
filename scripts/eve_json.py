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

from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, AlwaysTrueFilter, TimestampFilter
from suricatalog.log import DEFAULT_EVE
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO, parse_timestamp
from suricatalog.ui.app import one_shot_flow_table, host_data_use, get_agents

ALWAYS_TRUE = AlwaysTrueFilter()

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
    TIMESTAMP_FILTER = TimestampFilter()
    TIMESTAMP_FILTER.timestamp = OPTIONS.timestamp
    try:
        if OPTIONS.nxdomain:
            # eve_app.title = "DNS records with NXDOMAIN"
            filter = NXDomainFilter()
            pass
        elif OPTIONS.payload:
            # eve_app.title = "Inspect Alert Data (payload)"
            filter = WithPrintablePayloadFilter()
            pass
        elif OPTIONS.flow:
            eve_app = one_shot_flow_table(
                eve=OPTIONS.eve,
                data_filter=ALWAYS_TRUE
            )
        elif OPTIONS.netflow:
            eve_app = host_data_use(
                eve_files=OPTIONS.eve,
                data_filter=TIMESTAMP_FILTER,
                ip_address=OPTIONS.netflow.exploded
            )
        elif OPTIONS.useragent:
            eve_app = get_agents(
                eve_files=OPTIONS.eve,
                data_filter=TIMESTAMP_FILTER
            )
        eve_app.compose()
        eve_app.run()
    except KeyboardInterrupt:
        pass
