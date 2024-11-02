"""
Log file contents logic
"""
import json
import os
import time
from json import JSONDecodeError
from pathlib import Path
import logging
from typing import Callable, Dict

from suricatalog.filter import BaseFilter

DEFAULT_EVE = [Path("/var/log/suricata/eve.json")]
_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
_sc = logging.StreamHandler()
_sc.setFormatter(_fmt)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_sc)


def get_events_from_eve(
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
        eve_files = DEFAULT_EVE
    for eve_file in eve_files:
        try:
            with open(eve_file, 'rt', encoding='utf-8') as eve:
                for line in eve:
                    try:
                        data = json.loads(line)
                        if data_filter.accept(data):
                            yield data
                    except JSONDecodeError:
                        LOGGER.exception("I cannot use data: '%s'. Ignoring it.", line)
                        continue  # Try to read the next record
        except (FileNotFoundError, FileExistsError, UnicodeDecodeError) as ve:
            LOGGER.exception("I cannot use file %s. Ignoring it.", eve_file)
            raise ValueError(f"I cannot use {eve_file}. Ignoring it.", ve) from ve


def tail_eve(
        *,
        eve_file=None,
        decorator: Callable = json.loads
):
    """
    Similar to UNIX ``tail -f eve.json``
    :param decorator:
    :param eve_file:
    :return:
    """
    if eve_file is None:
        eve_file = DEFAULT_EVE
    try:
        with open(eve_file, 'rt', encoding='utf-8') as eve:
            eve.seek(0, os.SEEK_END)
            while True:
                try:
                    line = eve.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    data = decorator(line)
                    yield data
                except JSONDecodeError:
                    continue
    except (FileExistsError, UnicodeDecodeError) as ve:
        LOGGER.exception("I cannot use %s. Ignoring it.", eve_file)
        raise ValueError(f"I cannot use {eve_file}. Ignoring it.", ve) from ve
