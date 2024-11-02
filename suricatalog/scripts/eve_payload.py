"""
Application to extract payloads from Suricata eve log files.
:return:
"""
import argparse
from pathlib import Path

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import DEFAULT_EVE
from suricatalog.payload_app import PayloadApp


def main():
    """
    CLI entry point
    :return:
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--report_dir',
        type=Path,
        required=True,
        help="Directory where the payloads must be stored. Needs to exist."
    )
    parser.add_argument(
        'eve_file',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    options = parser.parse_args()
    try:
        if not options.report_dir.exists():
            raise ValueError(f"Please continue {options.report_dir} before we can proceed to extract the payloads.")
        app = PayloadApp(
            eve=options.eve_file,
            data_filter=WithPayloadFilter(),
            report_dir=options.report_dir
        )
        app.title = f"SuricataLog Payload extractor. Working on {','.join(x.as_posix() for x in options.eve_file)}. Results to {options.report_dir.as_posix()}"
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    """
    Entry level for CLI
    """
    main()
