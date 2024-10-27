"""
Unit test code
"""
import json
import unittest
from pathlib import Path

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import get_events_from_eve
from suricatalog.payload_app import extract_from_alert

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

    def test_generate_filename(self):
        with open(BASEDIR.parent / "test/eve_payload.json") as f:
            for line in f:
                payloads = json.loads(line)
                for payload in payloads:
                    self.assertIsNotNone(payload)
                    raise NotImplemented()

    def test_extract_from_alert(self):
        with open(BASEDIR.parent / "test/eve_payload.json") as f:
            for line in f:
                payloads = json.loads(line)
                self.assertIsNotNone(payloads)
                for payload_event in payloads:
                    extracted = extract_from_alert(alert=payload_event)
                    self.assertIsNotNone(extracted)


if __name__ == '__main__':
    unittest.main()
