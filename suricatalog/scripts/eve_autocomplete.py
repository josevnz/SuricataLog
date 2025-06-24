#!/usr/bin/env python
"""
Assist managing the SuricataLog auto complete features.

Note: Only Bash is supported on this version.

"""
import argparse
import logging
import shutil
from pathlib import Path

from suricatalog.time import DEFAULT_TIMESTAMP_20M_AGO

DEFAULT_BASH_AUTO_COMPLETE_SCRIPT = Path.home() / ".local/share/bash-completion/completions/suricata_log_bash_auto_complete.sh"
BASE_DIR = Path(__file__).resolve().parent
SOURCE_AUTOCOMPLETE = shutil.which("suricata_log_bash_auto_complete.sh")  # Use the deployed version.


def main():
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(fmt)
    logger = logging.getLogger(__name__)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Only --script can be combined with other options.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    exclusive_flags = parser.add_mutually_exclusive_group()
    exclusive_flags.add_argument(
        "--install",
        action='store_true',
        default=False,
        help=f"Install user autocomplete features ({SOURCE_AUTOCOMPLETE}).",
    )
    exclusive_flags.add_argument(
        "--remove",
        action='store_true',
        default=False,
        help="Remove user autocomplete features."
    )
    exclusive_flags.add_argument(
        "--timestamp",
        action='store_true',
        default=False,
        help=f"If called, print the timestamp from 10 minutes ago and exit. Now: '{DEFAULT_TIMESTAMP_20M_AGO}'"
    )
    parser.add_argument(
        "--script",
        action='store',
        type=Path,
        default=DEFAULT_BASH_AUTO_COMPLETE_SCRIPT,
        help=f"Override the installed destination of the autocomplete script.\nDefault: '{DEFAULT_BASH_AUTO_COMPLETE_SCRIPT}'"
    )
    options = parser.parse_args()
    if options.install:
        options.script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            src=SOURCE_AUTOCOMPLETE,
            dst=options.script,
            follow_symlinks=True
        )
        logger.info("Deployed from '%s' to '%s'", SOURCE_AUTOCOMPLETE, options.script)
    elif options.remove:
        if options.script.is_file():
            options.script.unlink()
            logger.info("Removed '%s'", options.script)
        else:
            logger.info("Nothing to remove.")
    elif options.timestamp:
        print(DEFAULT_TIMESTAMP_20M_AGO)
    else:
        print("Run again with '--help' to see available options.")


if __name__ == "__main__":
    main()
