"""
Unit test code for payload management
"""

import unittest
from pathlib import Path

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import get_events_from_eve
from suricatalog.payload_app import extract_from_alert, generate_filename

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
        payload_filter = WithPayloadFilter()
        payload_events = list(get_events_from_eve(
                eve_files=EVE_FILES,
                data_filter=payload_filter
        ))
        for payload_event in payload_events:
            self.assertIsNotNone(payload_event)
            filename = generate_filename(payload_data=payload_event)
            self.assertIsNotNone(filename)
            print(filename)

    async def test_extract_from_alert(self):
        payload_filter = WithPayloadFilter()
        payload_events = list(get_events_from_eve(
                eve_files=EVE_FILES,
                data_filter=payload_filter
        ))
        keys = {
            "timestamp",
            "dest_port",
            "src_ip",
            "dest_ip",
            "src_port",
            "payload"
        }
        for payload_event in payload_events:
            self.assertIsNotNone(payload_event)
            extracted = await extract_from_alert(alert=payload_event)
            self.assertIsNotNone(extracted)
            self.assertEqual(keys, set(extracted.keys()))
            payload = extracted['payload']
            self.assertIsNotNone(payload)


if __name__ == '__main__':
    unittest.main()
