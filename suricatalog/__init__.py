import json
from json import JSONDecodeError
from pathlib import Path
from typing import Dict, Any, Callable, Union
from datetime import datetime, timedelta

DEFAULT_TIMESTAMP_10M_AGO = datetime = datetime.now() - timedelta(minutes=10)
DEFAULT_EVE = [Path("/var/log/suricata/eve.json")]


def parse_timestamp(candidate: Union[str, Any]) -> datetime:
    """
    Expected something like 2022-02-08T16:32:14.900292+0000
    :param candidate:
    :return:
    """
    if isinstance(candidate, str):
        try:
            iso_candidate = candidate.split('+', 1)[0]
            return datetime.fromisoformat(iso_candidate)
        except ValueError:
            raise ValueError(f"Invalid date passed: {candidate}")
    elif isinstance(candidate, datetime):
        return candidate
    else:
        raise ValueError(f"I don't know how to handle {candidate}")


def alert_filter(
        *,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO,
        data: Dict[str, Any]
) -> bool:
    """
    Filter alerts on a given timestamp
    :param timestamp:
    :param data:
    :return:
    """
    if 'event_type' not in data:
        return False
    if data['event_type'] != 'alert':
        return False
    try:
        event_timestamp = parse_timestamp(data['timestamp'])
        if event_timestamp <= timestamp:
            return False
    except ValueError:
        return False
    return True


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
