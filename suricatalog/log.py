"""
Log file contents logic
"""
import json
from pathlib import Path
import logging
from typing import Dict
import orjson
from orjson import JSONDecodeError as OJSONDecodeError

from suricatalog.filter import BaseFilter

DEFAULT_EVE_JSON = [Path("/var/log/suricata/eve.json")]


class EveLogHandler:

    def __init__(self):
        _fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
        _sc = logging.StreamHandler()
        _sc.setFormatter(_fmt)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(_sc)

    def get_events(
            self,
            *,
            eve_files=None,
            data_filter: BaseFilter,
    ) -> Dict:
        """
        Get alerts from a JSON even file. Assumed each line is a valid
        JSON document, otherwise reader will crash
        :param eve_files:
        :param data_filter: Filter events based on several criteria
        :return:
        """
        if not isinstance(data_filter, BaseFilter):
            raise ValueError("Invalid 'data_filter' passed.")
        if eve_files is None:
            eve_files = DEFAULT_EVE_JSON

        for eve_file in eve_files:
            try:
                with open(eve_file, 'rt', encoding='utf-8') as eve:
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
