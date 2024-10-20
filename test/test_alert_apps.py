"""
Unit test for alert applications
"""
import logging
import unittest
from pathlib import Path

from suricatalog.alert_apps import TableAlertApp, BaseAlertApp
from suricatalog.filter import OnlyAlertsFilter, WithPrintablePayloadFilter
from suricatalog.log import get_events_from_eve

BASEDIR = Path(__file__).parent
EVE_FILES = [
    BASEDIR.joinpath("eve-2.json"),
    BASEDIR.joinpath("eve.json")
]
_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")
_sc = logging.StreamHandler()
_sc.setFormatter(_fmt)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_sc)


class AlertAppsTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Alert app unit test
    """
    async def test_extract_from_alert(self):
        """
        Text alert extraction
        :return:
        """
        for eve_file in EVE_FILES:
            events = get_events_from_eve(
                data_filter=WithPrintablePayloadFilter(),
                eve_files=[eve_file]
            )
            LOGGER.info("Processing %s", eve_file.as_posix())
            for event in events:
                brief_data = await BaseAlertApp.extract_from_alert(event)
                self.assertIsNotNone(brief_data)
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
        app.set_eve_files(EVE_FILES)
        app.set_filter(OnlyAlertsFilter())
        app.title = "Dummy title"
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Quit the app by pressing q
            await pilot.press("q")


if __name__ == '__main__':
    unittest.main()
