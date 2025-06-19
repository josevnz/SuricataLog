#!/usr/bin/env python
"""
Show Suricata alerts in different formats
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
from pathlib import Path

from suricatalog.alert_apps import TableAlertApp
from suricatalog.filter import BaseFilter, OnlyAlertsFilter
from suricatalog.log import DEFAULT_EVE_JSON
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO, parse_timestamp


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
        "--warnings",
        action="store_true",
        help="If passed, enable developer warnings for some events"
    )
    parser.add_argument(
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE_JSON[0]} file to parse."
    )
    options = parser.parse_args()
    timestamp_filter: BaseFilter = OnlyAlertsFilter()
    timestamp_filter.timestamp = options.timestamp
    try:
        app = TableAlertApp()
        app.title = f"SuricataLog Alerts (filter='>={options.timestamp}') for {','.join([eve.name for eve in options.eve_file])}"
        app.set_filter(timestamp_filter)
        app.set_eve_files(options.eve_file)
        if options.warnings:
            app.enable_developer_warnings = True
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    """
    Entry level CLI
    """
    main()
