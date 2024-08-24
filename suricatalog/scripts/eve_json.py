#!/usr/bin/env python
"""
This script is inspired by the examples provided on
[15.1.3. Eve JSON ‘jq’ Examples](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html)

A few things:
* The output uses colorized/ scrollable JSON
* You can filter by timestamp

"""

import argparse
import sys
from pathlib import Path
from ipaddress import ip_address

from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, AlwaysTrueFilter, TimestampFilter
from suricatalog.log import DEFAULT_EVE
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO, parse_timestamp
from suricatalog.canned import get_one_shot_flow_table, get_host_data_use, get_agents, get_capture

ALWAYS_TRUE = AlwaysTrueFilter()


def main():
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
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()
    TIMESTAMP_FILTER = TimestampFilter()
    TIMESTAMP_FILTER._timestamp = OPTIONS.timestamp
    try:
        if OPTIONS.nxdomain:
            eve_app = get_capture(
                eve=OPTIONS.eve_file,
                data_filter=NXDomainFilter(),
                title="SuricataLog DNS records with NXDOMAIN"
            )
        elif OPTIONS.payload:
            eve_app = get_capture(
                eve=OPTIONS.eve_file,
                data_filter=WithPrintablePayloadFilter(),
                title="SuricataLog Inspect Alert Data (payload)"
            )
        elif OPTIONS.flow:
            eve_app = get_one_shot_flow_table(
                eve=OPTIONS.eve_file,
                data_filter=ALWAYS_TRUE
            )
        elif OPTIONS.netflow:
            eve_app = get_host_data_use(
                eve_files=OPTIONS.eve_file,
                data_filter=TIMESTAMP_FILTER,
                ip_address=OPTIONS.netflow.exploded
            )
        elif OPTIONS.useragent:
            eve_app = get_agents(
                eve_files=OPTIONS.eve_file,
                data_filter=TIMESTAMP_FILTER
            )
        else:
            PARSER.print_usage()
            sys.exit(0)
        eve_app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
