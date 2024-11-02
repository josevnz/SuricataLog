"""
Unit tests for mini apps
"""
import unittest
from ipaddress import ip_address
from pathlib import Path

from textual.widgets import RichLog, DataTable, Digits

from suricatalog.canned import get_capture, get_one_shot_flow_table, get_host_data_use, get_agents
from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, TimestampFilter
from suricatalog.scripts.eve_json import ALWAYS_TRUE
from suricatalog.time import DEFAULT_TIMESTAMP_10Y_AGO

BASEDIR = Path(__file__).parent
EVE_FILE = BASEDIR.joinpath("eve.json")
EVE_UDP_FILE = BASEDIR.joinpath("eve_udp_flow.json")
OLD_DATE = DEFAULT_TIMESTAMP_10Y_AGO


class MiniAppsTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Concrete implementation of unit test for mini apps
    """
    async def test_get_capture(self):
        """
        Simulate user iteration with mini apps
        :return:
        """
        app = get_capture(
            eve=[EVE_FILE],
            data_filter=NXDomainFilter(),
            title="SuricataLog DNS records with NXDOMAIN"
        )
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            log = app.screen.query(RichLog).first()
            self.assertIsNotNone(log)
            self.assertEqual("        'rrtype': 'A',", log.lines[99].text)
            await pilot.pause()
            await pilot.press("q")

            app = get_capture(
                eve=[EVE_FILE],
                data_filter=WithPrintablePayloadFilter(),
                title="SuricataLog Inspect Alert Data (payload)"
            )
            self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            log = app.screen.query(RichLog).first()
            self.assertIsNotNone(log)
            self.assertRegex("{", log.lines[0].text)
            await pilot.pause()
            await pilot.press("q")

    async def test_get_one_shot_flow_table(self):
        """
        Test one shot table app
        :return:
        """
        app = get_one_shot_flow_table(
            eve=[EVE_FILE],
            data_filter=ALWAYS_TRUE
        )
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            table = app.query(DataTable).first()
            self.assertIsNotNone(table)
            coordinate = table.cursor_coordinate
            self.assertTrue(table.is_valid_coordinate(coordinate))
            data = table.get_cell_at(coordinate)
            self.assertEqual("TCP", data)
            await pilot.pause()
            await pilot.press("q")

    async def test_get_host_data_use(self):
        """
        Test get host data app
        :return:
        """
        ts = TimestampFilter()
        ts.timestamp = DEFAULT_TIMESTAMP_10Y_AGO
        app = get_host_data_use(
            eve_files=[EVE_UDP_FILE],
            data_filter=ts,
            ip_address=ip_address('224.0.0.251')
        )
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            netflow = app.query(Digits).first()
            self.assertIsNotNone(netflow)
            self.assertEqual('0 bytes', netflow.value)
            await pilot.pause()
            await pilot.press("q")

    async def test_get_agents(self):
        """
        Test get agents app
        :return:
        """
        ts = TimestampFilter()
        ts.timestamp = DEFAULT_TIMESTAMP_10Y_AGO
        app = get_agents(
            eve_files=[EVE_FILE],
            data_filter=ts
        )
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            log = app.screen.query(RichLog).first()
            self.assertIsNotNone(log)
            self.assertRegex("{", log.lines[0].text)
            await pilot.pause()
            await pilot.press("q")


if __name__ == '__main__':
    unittest.main()
