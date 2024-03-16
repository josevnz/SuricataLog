#!/usr/bin/env python
"""
Show Suricata alerts in different formats
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
from pathlib import Path

from suricatalog.filter import BaseFilter, OnlyAlertsFilter
from suricatalog.alert_apps import TableAlertApp
from suricatalog.time import parse_timestamp, DEFAULT_TIMESTAMP_10Y_AGO
from suricatalog.log import DEFAULT_EVE


def main():
    PARSER = argparse.ArgumentParser(description=__doc__)
    PARSER.add_argument(
        "--timestamp",
        type=parse_timestamp,
        default=DEFAULT_TIMESTAMP_10Y_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10Y_AGO})"
    )
    PARSER.add_argument(
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()
    timestamp_filter: BaseFilter = OnlyAlertsFilter()
    timestamp_filter.timestamp = OPTIONS.timestamp
    try:
        app = TableAlertApp()
        app.title = f"SuricataLog Alerts (filter='>={OPTIONS.timestamp}') for {','.join([eve.name for eve in OPTIONS.eve_file])}"
        app.set_filter(timestamp_filter)
        app.set_eve_files(OPTIONS.eve_file)
        app.run()
    except KeyboardInterrupt:
        raise


if __name__ == "__main__":
    main()
