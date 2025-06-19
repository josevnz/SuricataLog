"""
Eve log file contents logic
"""
import json
import logging
from pathlib import Path

import orjson
from orjson import JSONDecodeError as OJSONDecodeError

from suricatalog.filter import BaseFilter

DEFAULT_EVE_JSON = [Path("/var/log/suricata/eve.json")]


class EveLogHandler:
    """
    Handle processing of eve.json files
    """

    def __init__(
            self,
            log_file: Path | str | None = None
    ):
        """
        :param log_file: If set logs will be written to a file
        """
        fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
        log_handler = None
        if log_file:
            if isinstance(log_file, str):
                log_file = Path(log_file)
            if log_file.parent.exists() and log_file.parent.is_dir():
                log_handler = logging.FileHandler(filename=log_file)
        if not log_handler:  # Still no log_handler
            log_handler = logging.StreamHandler()
        log_handler.setFormatter(fmt)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(log_handler)
        self.logger.setLevel(logging.INFO)

    def get_events(
            self,
            *,
            eve_files=None,
            data_filter: BaseFilter,
    ) -> dict:
        """
        Get alerts from a JSON even file. Assumed each line is a valid
        JSON document, otherwise reader will crash
        :param eve_files:
        :param data_filter: Filter events based on several criteria
        :return: Dictionary with events
        """
        if not isinstance(data_filter, BaseFilter):
            raise ValueError("Invalid 'data_filter' passed.")
        if eve_files is None:
            eve_files = DEFAULT_EVE_JSON

        for eve_file in eve_files:
            try:
                with open(eve_file, encoding='utf-8') as eve:
                    for line in eve:
                        try:
                            data = orjson.loads(
                                line
                            )
                            if data_filter.accept(data):
                                yield data
                        except OJSONDecodeError:
                            try:
                                data = json.loads(line)
                                if data_filter.accept(data):
                                    yield data
                            except json.JSONDecodeError:
                                self.logger.exception("I cannot use data: '%s'. Ignoring it.", line)
                                continue  # Try to read the next record
            except (FileNotFoundError, FileExistsError, UnicodeDecodeError):
                self.logger.exception("I cannot use file '%s'. Ignoring it.", eve_file)
