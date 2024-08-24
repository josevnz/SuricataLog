from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from suricatalog.time import DEFAULT_TIMESTAMP_10M_AGO, parse_timestamp, to_utc


class BaseFilter(ABC):
    @abstractmethod
    def accept(self, data: Dict[Any, Any]) -> bool:
        raise NotImplementedError()


class AlwaysTrueFilter(BaseFilter):

    def accept(self, data: Dict[Any, Any]) -> bool:
        return True


class OnlyAlertsFilter(BaseFilter):

    def __init__(self):
        self._timestamp = DEFAULT_TIMESTAMP_10M_AGO

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        if not timestamp:
            raise ValueError("Missing timestamp")
        if not self.timestamp.tzinfo:
            raise ValueError(f"{timestamp} has not TimeZone information")
        self._timestamp = timestamp

    def accept(self, data: Dict[Any, Any]) -> bool:
        try:
            event_timestamp = parse_timestamp(data['timestamp'])
            if event_timestamp <= self._timestamp:
                return False
            if 'event_type' in data and 'alert' == data['event_type']:
                return True
            return False
        except ValueError:
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
        if 'event_type' in data and 'alert' == data['event_type']:
            if 'payload_printable' in data and data['payload_printable'] and data['payload_printable'] != 'null':
                return True
            elif 'payload' in data and data['payload'] and data['payload'] != 'null':
                return True
        return False


class TimestampFilter(BaseFilter):

    def __init__(self):
        self._timestamp = DEFAULT_TIMESTAMP_10M_AGO

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        if not timestamp:
            raise ValueError("Missing timestamp")
        if not timestamp.tzinfo:
            raise ValueError(f"{timestamp} has not TimeZone information")
        self._timestamp = timestamp

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        Filter events on a given timestamp
        :param data:
        :return:
        """
        try:
            event_timestamp = parse_timestamp(data['timestamp'])
            if not event_timestamp.tzinfo:
                event_timestamp = to_utc(event_timestamp)
            if event_timestamp <= self._timestamp:
                return False
        except TypeError:
            if not self._timestamp.tzinfo:
                raise TypeError(f"today timestamp={self._timestamp} has not TimeZone information.")
        except ValueError:
            return False
        return True

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value
