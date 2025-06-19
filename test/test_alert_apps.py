"""
Unit test for alert applications
"""

import bz2
import logging
import tempfile
import unittest
from pathlib import Path

from suricatalog.alert_apps import BaseAlertApp, TableAlertApp
from suricatalog.filter import OnlyAlertsFilter, WithPrintablePayloadFilter
from suricatalog.log import EveLogHandler

BASEDIR = Path(__file__).parent
_fmt = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
)
_sc = logging.StreamHandler()
_sc.setFormatter(_fmt)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_sc)
WANTED_KEYS = [
    "timestamp",
    "dest_port",
    "src_ip",
    "dest_ip",
    "src_port",
    "protocol",
    "severity",
    "signature",
    "payload_printable",
]


class AlertAppsTestCase(unittest.IsolatedAsyncioTestCase):
    huge_eve_file: tempfile.NamedTemporaryFile

    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile(
            mode="wb", dir="/var/tmp", prefix="eve_large-", suffix=".json", delete=False
        ) as test_temp_file:
            large_eve_compressed = Path(BASEDIR) / "eve_large.json.bz2"
            data = bz2.BZ2File(large_eve_compressed).read()
            cls.huge_eve_file = test_temp_file
            cls.huge_eve_file.write(data)
            cls.eve_files = [
                BASEDIR.joinpath("eve-2.json"),
                BASEDIR.joinpath("eve.json"),
                Path(cls.huge_eve_file.name),
            ]

    @classmethod
    def tearDownClass(cls):
        Path(cls.huge_eve_file.name).unlink()

    """
    Alert app unit test
    """

    async def test_extract_from_alert(self):
        """
        Text alert extraction
        :return:
        """
        for eve_file in AlertAppsTestCase.eve_files:
            with self.subTest(eve_file=eve_file):
                events = EveLogHandler().get_events(
                    data_filter=WithPrintablePayloadFilter(), eve_files=[eve_file]
                )
                LOGGER.info("Processing %s", eve_file.as_posix())

                for event in events:
                    brief_data = await BaseAlertApp.extract_from_alert(event)
                    self.assertIsNotNone(brief_data)
                    for key in WANTED_KEYS:
                        self.assertIn(key, brief_data)
                    LOGGER.info("%s", brief_data)

    """
    Concrete unit test for alert app
    """

    async def test_eve_log(self):
        """
        Simulate user iteration with the alert app
        :return:
        """
        app = TableAlertApp()
        app.set_eve_files(AlertAppsTestCase.eve_files)
        app.set_filter(OnlyAlertsFilter())
        app.title = "Dummy title"
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Quit the app by pressing q
            await pilot.press("q")


if __name__ == "__main__":
    unittest.main()
