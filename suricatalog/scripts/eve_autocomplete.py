#!/usr/bin/env python
"""
Assist managing the SuricataLog auto complete features.

Note: Only Bash is supported on this version.

"""
import argparse
from pathlib import Path

DEFAULT_BASH_AUTO_COMPLETE_SCRIPT = Path.home() / ".local/share/bash-completion/completions/suricata_log_bash_auto_complete.sh"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="You must choose either '--install' or '--remove'.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    exclusive_flags = parser.add_mutually_exclusive_group()
    exclusive_flags.add_argument(
        "--install",
        action='store_true',
        default=False,
        help="Install user autocomplete features.",
    )
    exclusive_flags.add_argument(
        "--remove",
        action='store_true',
        default=False,
        help="Remove user autocomplete features."
    )
    exclusive_flags.add_argument(
        "--script",
        action='store',
        type=Path,
        default=DEFAULT_BASH_AUTO_COMPLETE_SCRIPT,
        help=f"Override the installed destination of the autocomplete script.\nDefault: {DEFAULT_BASH_AUTO_COMPLETE_SCRIPT}"
    )
    options = parser.parse_args()

    if options.install:
        pass
    elif options.remove:
        pass
    else:
        print("Run again with '--help' to see available options.")


if __name__ == "__main__":
    main()
