"""
Unit test for logging
"""

import bz2
import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import orjson
import pytz

from suricatalog.filter import AlwaysTrueFilter, OnlyAlertsFilter, TimestampFilter
from suricatalog.log import EveLogHandler
from suricatalog.time import parse_timestamp, to_utc

BASEDIR = Path(__file__).parent


class SuricataLogTestCase(unittest.TestCase):
    """
    Unit test for suricata log common tests
    """

    eve_list = []
    old_date = datetime(year=2021, day=2, month=8, tzinfo=pytz.UTC)
    huge_eve_file: tempfile.NamedTemporaryFile

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup data loading
        :return:
        """
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
        )
        cls.logger = logging.getLogger("SuricataLogTestCase")
        cls.logger.setLevel(logging.INFO)
        with open(BASEDIR.joinpath("eve.json"), encoding="utf-8") as eve_file:
            for event in eve_file:
                SuricataLogTestCase.eve_list.append(orjson.loads(event))
        cls.logger.info("Loaded eve %s", "eve.json")

        large_eve_compressed = Path(BASEDIR) / "eve_large.json.bz2"
        data = bz2.BZ2File(large_eve_compressed).read()
        cls.logger.info(
            "Uncompressed and loaded %s", large_eve_compressed.resolve().as_posix()
        )
        with tempfile.NamedTemporaryFile(
            mode="wb", dir="/var/tmp", prefix="eve_large-", suffix=".json", delete=False
        ) as test_temp_file:
            test_temp_file.write(data)
            cls.huge_eve_file = test_temp_file
            cls.logger.info("Wrote %s", cls.huge_eve_file.name)

    @classmethod
    def tearDownClass(cls):
        Path(cls.huge_eve_file.name).unlink()
        cls.logger.info("Removed %s", cls.huge_eve_file.name)

    def test_to_utc(self):
        """
        Test UCT datetime handling
        :return:
        """
        naive = datetime.now()
        non_naive = datetime(year=2024, day=2, month=2, tzinfo=pytz.UTC)
        dates = [naive, non_naive]
        for test_date in dates:
            ts = to_utc(test_date)
            self.assertTrue(ts)
            self.assertIsInstance(ts, datetime)
            self.assertIsNotNone(ts.tzinfo)

    def test_parse_timestamp(self):
        """
        Test timestamp parsing
        :return:
        """
        invalid = "XXX-02-08T16:32:14.900292"
        naive = datetime.now()
        non_naive = datetime(year=2024, day=2, month=2, tzinfo=pytz.UTC)
        dates = [
            "2022-02-08T16:32:14.900292+0000",
            "2022-02-08 16:32:14.900292+0000",
            "2022-02-08T16:32:14.900292",
            naive,
            non_naive,
            invalid,
        ]
        for idx, test_date in enumerate(dates):
            try:
                ts = parse_timestamp(test_date)
                self.assertTrue(ts)
                self.assertIsInstance(ts, datetime)
                self.assertIsNotNone(ts.tzinfo)
            except ValueError:
                if idx == 6:
                    self.fail(
                        f"Was supposed to fail with an invalid timestamp: {invalid}"
                    )
                else:
                    pass

    def test_timestamp_filter(self):
        """
        Test timestamp filtering
        :return:
        """
        timestamp_filter = TimestampFilter()
        timestamp_filter.timestamp = SuricataLogTestCase.old_date
        self.assertTrue(timestamp_filter.accept(data=SuricataLogTestCase.eve_list[0]))
        self.assertTrue(timestamp_filter.accept(data=SuricataLogTestCase.eve_list[132]))

    def test_get_alerts(self):
        """
        Test get alerts
        :return:
        """
        timestamp_filter = TimestampFilter()
        timestamp_filter.timestamp = SuricataLogTestCase.old_date
        all_alerts = [
            x
            for x in EveLogHandler().get_events(
                eve_files=[BASEDIR.joinpath("eve.json")], data_filter=timestamp_filter
            )
            if x["event_type"] == "alert"
        ]
        self.assertIsNotNone(all_alerts)
        self.assertEqual(275, len(all_alerts))
        self.assertEqual(
            "SURICATA Applayer Detect protocol only one direction",
            all_alerts[90]["alert"]["signature"],
        )

    def test_get_all_events(self):
        """
        Test get all event, unfiltered
        :return:
        """
        always_true_filter = AlwaysTrueFilter()
        eve_lh = EveLogHandler()
        all_events = list(
            eve_lh.get_events(
                eve_files=[BASEDIR.joinpath("eve.json")], data_filter=always_true_filter
            )
        )
        self.assertIsNotNone(all_events)
        self.assertListEqual(SuricataLogTestCase.eve_list, all_events)

        all_events = list(
            eve_lh.get_events(
                eve_files=[
                    BASEDIR.joinpath("eve.json"),
                    BASEDIR.joinpath("eve-2.json"),
                ],
                data_filter=always_true_filter,
            )
        )
        self.assertIsNotNone(all_events)
        self.assertEqual(len(all_events), 9436)

        all_events = list(
            eve_lh.get_events(
                eve_files=[Path(self.__class__.huge_eve_file.name)],
                data_filter=always_true_filter,
            )
        )
        self.assertIsNotNone(all_events)
        self.assertEqual(len(all_events), 40231)

    def test_get_only_alerts(self):
        only_alerts_filter = OnlyAlertsFilter()
        only_alerts_filter.timestamp = SuricataLogTestCase.old_date

        # Testing files as separate groups to make it easier to spot issues.
        files = [
            BASEDIR.joinpath("eve.json"),
            BASEDIR.joinpath("eve-2.json"),
            Path(self.__class__.huge_eve_file.name),
        ]
        eve_lh = EveLogHandler()
        for file in files:
            with self.subTest(file=files):
                self.__class__.logger.info("Testing %s", file.resolve().as_posix())
                for alert in eve_lh.get_events(
                    eve_files=[file], data_filter=only_alerts_filter
                ):
                    self.assertIsNotNone(alert)
                    alert_keys = alert.keys()
                    for keyword in ["alert"]:
                        self.assertIn(keyword, alert_keys)
                        sub_keys = alert["alert"].keys()
                        for expected_subkey in ["signature", "severity"]:
                            self.assertIn(expected_subkey, sub_keys)


if __name__ == "__main__":
    unittest.main()
