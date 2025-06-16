"""
Unit test code for payload management
"""
import tempfile
import unittest
from pathlib import Path

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import get_events_from_eve
from suricatalog.payload_app import PayloadApp

BASEDIR = Path(__file__).parent
EVE_FILES = [
    BASEDIR.joinpath("eve.json"),
    BASEDIR.joinpath("eve-2.json")
]

PAYLOAD_FILES = [
    BASEDIR.joinpath("eve_payload.json")
]


class PayloadTestCase(unittest.IsolatedAsyncioTestCase):

    """
    Payload unit tests
    """

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
        self.assertEqual(131, len(payload_events))

    async def test_generate_filename(self):
        """
        Make sure generated test filename is correct
        :return:
        """
        payload_filter = WithPayloadFilter()
        payload_events = list(get_events_from_eve(
                eve_files=EVE_FILES,
                data_filter=payload_filter
        ))
        for payload_event in payload_events:
            self.assertIsNotNone(payload_event)
            extracted = await PayloadApp.extract_from_alert(alert=payload_event)
            filename = PayloadApp.generate_filename(
                base_dir=Path.home(),
                payload_data=extracted
            )
            self.assertIsNotNone(filename)
            # print(filename)

    async def test_extract_from_alert(self):
        """
        Check if payload filer can extract payload from alert
        :return:
        """
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
            "payload",
            "signature"
        }
        for payload_event in payload_events:
            self.assertIsNotNone(payload_event)
            extracted = await PayloadApp.extract_from_alert(alert=payload_event)
            self.assertIsNotNone(extracted)
            self.assertEqual(keys, set(extracted.keys()))
            payload = extracted['payload']
            self.assertIsNotNone(payload)

    async def test_save_fake_payload(self):
        """
        Test if payload can be saved
        :return:
        """
        with tempfile.NamedTemporaryFile(delete=True) as tmpdir:
            payload = {'payload': "FakeData"}
            saved = await PayloadApp.save_payload(
                payload_file=Path(tmpdir.name),
                payload=payload
            )
            self.assertEqual(8, saved)

    async def test_save_payload_from_file(self):
        """
        Test if payload can be extracted and then saved to a temporary file
        :return:
        """
        payload_filter = WithPayloadFilter()
        for event_with_payload in get_events_from_eve(eve_files=PAYLOAD_FILES, data_filter=payload_filter):
            self.assertIsNotNone(event_with_payload)
            extracted = await PayloadApp.extract_from_alert(alert=event_with_payload)
            self.assertIsNotNone(extracted)
            with tempfile.NamedTemporaryFile(delete=True) as tmpdir:
                temp_filename = Path(tmpdir.name).resolve()
                length_saved = await PayloadApp.save_payload(payload_file=temp_filename, payload=event_with_payload)
                self.assertGreater(length_saved, 0)


if __name__ == '__main__':
    unittest.main()
