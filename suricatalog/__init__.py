from typing import Dict, Any
from datetime import datetime

from suricatalog.time import parse_timestamp, DEFAULT_TIMESTAMP_10M_AGO


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


