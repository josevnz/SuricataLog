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


class OnlyAlertsFilter(BaseFilter):

    def accept(self, data: Dict[Any, Any]) -> bool:
        if 'event_type' in data and 'alert' == data['event_type']:
            return True
        return False


class NXDomainFilter(BaseFilter):

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        tail -f eve.json|jq -c 'select(.dns.rcode=="NXDOMAIN")'
        """
        if 'dns' in data and 'rcode' in data['dns'] and data['dns']['rcode'] == 'NXDOMAIN':
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
        **_
) -> bool:
    """
    Always true filter
    :return:
    """
    return True


def timestamp_filter(
        *,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO,
        data: Dict[str, Any]
) -> bool:
    """
    Filter events on a given timestamp
    :param timestamp:
    :param data:
    :return:
    """
    try:
        event_timestamp = parse_timestamp(data['timestamp'])
        if event_timestamp <= timestamp:
            return False
    except ValueError:
        return False
    return True
