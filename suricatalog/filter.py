from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from suricatalog.time import DEFAULT_TIMESTAMP_10M_AGO, parse_timestamp


class BaseFilter(ABC):
    @abstractmethod
    def accept(self, data: Dict[Any, Any]) -> bool:
        raise NotImplementedError()


class AlwaysTrueFilter(BaseFilter):

    def accept(self, data: Dict[Any, Any]) -> bool:
        return True


class NXDomainFilter(BaseFilter):

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        tail -f eve.json|jq -c 'select(.dns.rcode=="NXDOMAIN")'
        """
        if 'dns' in data and data['dns']['rcode'] == 'NXDOMAIN':
            return True
        return False


class WithPrintablePayloadFilter(BaseFilter):
    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        cat ~/SuricataLog/test/eve.json | jq -r -c 'select(.event_type=="alert")|.payload'|base64 --decode
        :param data:
        :return:
        """
        if 'event_type' in data and 'alert' == data['event_type'] and data['payload_printable']:
            return True
        return False


def all_events_filter(
        *,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO,
        data: Dict[str, Any]
) -> bool:
    """
    Always true filter
    :param timestamp:
    :param data:
    :return:
    """
    return True


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
