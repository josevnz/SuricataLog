import unittest
from pathlib import Path

from suricatalog.alert_apps import TableAlertApp
from suricatalog.filter import BaseFilter, OnlyAlertsFilter

BASEDIR = Path(__file__).parent
EVE_FILE = BASEDIR.joinpath("eve.json")


class AlertAppsTestCase(unittest.TestCase):
    async def test_eve_log(self):
        timestamp_filter: BaseFilter = OnlyAlertsFilter()
        app = TableAlertApp()
        app.title = "Dummy title"
        app.set_filter(timestamp_filter)
        app.set_eve_files([EVE_FILE])
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            pass


if __name__ == '__main__':
    unittest.main()
