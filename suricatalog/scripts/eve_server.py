"""
Wrapper to execute eve CLI applications from a web browser.
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)

Examples:

   eve_server --application eve_json -- --flow ~/eve.json
   eve_server --application eve_json -- --nxdomain ~/eve.json
   eve_server --applications eve_log -- ~/eve.json

The -- is necessary to be able to process flags on all the other eve_* applications.

"""
import argparse

from textual_serve.server import Server

ALLOWED_APPS = [
    "eve_json",
    "eve_log"
]
PORT = 8000


def main():
    """
    Entry point for wrapper
    :return:
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        exit_on_error=False
    )
    parser.add_argument(
        "--application",
        action='store',
        choices=ALLOWED_APPS,
        default=ALLOWED_APPS[0],
        help=f"Allowed applications: {', '.join(ALLOWED_APPS)}"
    )
    parser.add_argument(
        "--port",
        action='store',
        default=PORT,
        required=False,
        help=f"Override port: {PORT}"
    )
    parser.add_argument(
        "--debug",
        action='store_true',
        default=False,
        help="Enable debug mode"
    )
    parser.add_argument(
        "eve_remainder",
        action='store',
        nargs=argparse.ZERO_OR_MORE,
        help="Arguments specific to suricata applications. Try passing --help"
    )

    options = parser.parse_args()
    cmd = f"{options.application} {' '.join(list(options.eve_remainder))}"
    server = Server(
        port=options.port,
        command=cmd,
        title="Suricatalog Server",
    )
    server.serve(options.debug)


if __name__ == "__main__":
    main()
