import json
import os
import time
from json import JSONDecodeError
from pathlib import Path
from typing import Callable, Dict

from suricatalog import alert_filter, datetime, DEFAULT_TIMESTAMP_10M_AGO

DEFAULT_EVE = [Path("/var/log/suricata/eve.json")]


def get_alerts_from_eve(
        *,
        eve_files=None,
        row_filter: Callable = alert_filter,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO
) -> Dict:
    """
    Get alerts from a JSON even file
    :param eve_files:
    :param row_filter:
    :param timestamp:
    :return:
    """
    if eve_files is None:
        eve_files = DEFAULT_EVE
    for eve_file in eve_files:
        with open(eve_file, 'rt') as eve:
            for line in eve:
                try:
                    data = json.loads(line)
                    if row_filter(data=data, timestamp=timestamp):
                        yield data
                except JSONDecodeError:
                    continue  # Try to read the next record


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
    with open(eve_file, 'rt') as eve:
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
