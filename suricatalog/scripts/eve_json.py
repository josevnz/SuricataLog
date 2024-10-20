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
    """
    CLI entry point
    :return:
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timestamp",
        type=parse_timestamp,
        default=DEFAULT_TIMESTAMP_10Y_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10Y_AGO})"
    )
    exclusive_flags = parser.add_mutually_exclusive_group()
    exclusive_flags.add_argument(
        "--nxdomain",
        action='store_true',
        default=False,
        help="Show DNS records with NXDOMAIN"
    )
    exclusive_flags.add_argument(
        "--payload",
        action='store_true',
        default=False,
        help="Show alerts with a printable payload"
    )
    exclusive_flags.add_argument(
        "--flow",
        action='store_true',
        default=False,
        help="Aggregated flow report per protocol and destination port"
    )
    exclusive_flags.add_argument(
        "--netflow",
        type=ip_address,
        action='store',
        help="Get the netflow for a given IP address"
    )
    exclusive_flags.add_argument(
        "--useragent",
        action='store_true',
        default=False,
        help="Top user agent in HTTP traffic"
    )
    parser.add_argument(
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    options = parser.parse_args()
    timestamp_filter = TimestampFilter()
    timestamp_filter.timestamp = options.timestamp
    try:
        if options.nxdomain:
            eve_app = get_capture(
                eve=options.eve_file,
                data_filter=NXDomainFilter(),
                title="SuricataLog DNS records with NXDOMAIN"
            )
        elif options.payload:
            eve_app = get_capture(
                eve=options.eve_file,
                data_filter=WithPrintablePayloadFilter(),
                title="SuricataLog Inspect Alert Data (payload)"
            )
        elif options.flow:
            eve_app = get_one_shot_flow_table(
                eve=options.eve_file,
                data_filter=ALWAYS_TRUE
            )
        elif options.netflow:
            eve_app = get_host_data_use(
                eve_files=options.eve_file,
                data_filter=timestamp_filter,
                ip_address=options.netflow.exploded
            )
        elif options.useragent:
            eve_app = get_agents(
                eve_files=options.eve_file,
                data_filter=timestamp_filter
            )
        else:
            parser.print_usage()
            sys.exit(0)
        eve_app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
