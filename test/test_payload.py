"""
Unit test code
"""
import json
import unittest
from pathlib import Path

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import get_events_from_eve

BASEDIR = Path(__file__).parent
EVE_FILES = [
    BASEDIR.joinpath("eve.json"),
    BASEDIR.joinpath("eve-2.json")
]


class PayloadTestCase(unittest.IsolatedAsyncioTestCase):

    def test_get_payload_events(self):
        """
        Test get all event, unfiltered
        :return:
        """
        payload_filter = WithPayloadFilter()
        payload_events = list(get_events_from_eve(
            eve_files=EVE_FILES,
            data_filter=payload_filter
        ))
        self.assertIsNotNone(payload_events)
        self.assertEquals(131, len(payload_events))




if __name__ == '__main__':
    unittest.main()
