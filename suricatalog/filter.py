"""
Common filtering logic
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from suricatalog.time import DEFAULT_TIMESTAMP_10M_AGO, parse_timestamp, to_utc


class BaseFilter(ABC):
    """
    Abstract filter
    """

    @abstractmethod
    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        Needs to be overridden with real logic
        :param data:
        :return:
        """
        raise NotImplementedError()


class AlwaysTrueFilter(BaseFilter):
    """
    This filter is always true
    """

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        Always true implementation
        :param data:
        :return:
        """
        return True


class OnlyAlertsFilter(BaseFilter):
    """
    Filter only alerts
    """

    def __init__(self):
        """
        Constructor
        """
        self._timestamp = DEFAULT_TIMESTAMP_10M_AGO

    @property
    def timestamp(self):
        """
        Get timestamp
        :return:
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        """
        Set timestamp
        :param timestamp:
        :return:
        """
        if not timestamp:
            raise ValueError("Missing timestamp")
        if not self.timestamp.tzinfo:
            raise ValueError(f"{timestamp} has not TimeZone information")
        self._timestamp = timestamp

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        Filter events based on time and only alerts
        :param data:
        :return:
        """
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
    """
    Filter for DNS code
    """

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        tail -f eve.json|jq -c 'select(.dns.rcode=="NXDOMAIN")'
        """
        if 'dns' in data and 'rcode' in data['dns'] and data['dns']['rcode'] == 'NXDOMAIN':
            return True
        return False


class WithPrintablePayloadFilter(BaseFilter):
    """
    Show only records with a printable payload
    """

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        cat ~/SuricataLog/test/eve.json | jq -r -c 'select(.event_type=="alert")|.payload'|base64 --decode
        :param data:
        :return:
        """
        if 'event_type' in data and 'alert' == data['event_type']:
            payload_printable = 'payload_printable' in data and data['payload_printable'] and data[
                'payload_printable'] != 'null'
            has_payload = 'payload' in data and data['payload'] and data['payload'] != 'null'
            if payload_printable or has_payload:
                return True
        return False


class TimestampFilter(BaseFilter):
    """
    Filter for events based on timestamp
    """

    def __init__(self):
        self._timestamp = DEFAULT_TIMESTAMP_10M_AGO

    @property
    def timestamp(self):
        """
        Get timestamps
        :return:
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        """"
        Set timestamp
        """
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
        except TypeError as te:
            if not self._timestamp.tzinfo:
                raise TypeError(f"today timestamp={self._timestamp} has not TimeZone information.") from te
        except ValueError:
            return False
        return True


class WithPayloadFilter(BaseFilter):
    """
    Filter records with any payload
    """

    def accept(self, data: Dict[Any, Any]) -> bool:
        """
        cat ~/SuricataLog/test/eve.json | jq -r -c 'select(.event_type=="alert")|.payload'|base64 --decode
        :param data:
        :return:
        """
        if 'event_type' in data and 'alert' == data['event_type']:
            payload = 'payload' in data and data['payload'] and data[
                'payload'] != 'null'
            if payload:
                return True
        return False
