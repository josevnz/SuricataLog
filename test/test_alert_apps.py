"""
Unit test for alert applications
"""
import unittest
from pathlib import Path

from suricatalog.alert_apps import TableAlertApp
from suricatalog.filter import OnlyAlertsFilter

BASEDIR = Path(__file__).parent
EVE_FILE = BASEDIR.joinpath("eve.json")


class AlertAppsTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Concrete unit test for alert app
    """
    async def test_eve_log(self):
        """
        Simulate user iteration with the alert app
        :return:
        """
        app = TableAlertApp()
        app.set_eve_files([EVE_FILE])
        app.set_filter(OnlyAlertsFilter())
        app.title = "Dummy title"
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Quit the app by pressing q
            await pilot.press("q")


if __name__ == '__main__':
    unittest.main()
