#!/usr/bin/env python
"""
Show Suricata alerts in different formats
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
from pathlib import Path

from suricatalog.filter import BaseFilter, WithPrintablePayloadFilter
from suricatalog.alert_apps import TableAlertApp
from suricatalog.time import parse_timestamp, DEFAULT_TIMESTAMP_10Y_AGO
from suricatalog.log import DEFAULT_EVE


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
    parser.add_argument(
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    options = parser.parse_args()
    timestamp_filter: BaseFilter = WithPrintablePayloadFilter()
    timestamp_filter.timestamp = options.timestamp
    try:
        app = TableAlertApp()
        app.title = f"SuricataLog Alerts (filter='>={options.timestamp}') for {','.join([eve.name for eve in options.eve_file])}"
        app.set_filter(timestamp_filter)
        app.set_eve_files(options.eve_file)
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    """
    Entry level CLI
    """
    main()
