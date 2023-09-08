#!/usr/bin/env python
"""
Show Suricata alerts in different formats
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
from pathlib import Path

from suricatalog.time import parse_timestamp, DEFAULT_TIMESTAMP_10Y_AGO
from suricatalog.log import DEFAULT_EVE
from ui.utility import Formats, get_format, FORMATS

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description=__doc__)
    PARSER.add_argument(
        "--timestamp",
        type=parse_timestamp,
        default=DEFAULT_TIMESTAMP_10Y_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10Y_AGO})"
    )
    PARSER.add_argument(
        "--formats",
        type=get_format,
        default=Formats.TABLE,
        choices=FORMATS,
        help="Choose the output format"
    )
    PARSER.add_argument(
        'eve',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()
    try:
        if OPTIONS.formats == Formats.TABLE:
            raise NotImplementedError()
        elif OPTIONS.formats == Formats.BRIEF:
            raise NotImplementedError()
        else:
            raise NotImplementedError()
    except KeyboardInterrupt:
        raise
