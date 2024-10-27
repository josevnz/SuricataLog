"""
Unit test for logging
"""
import json
import unittest
from datetime import datetime
from pathlib import Path

import pytz

from suricatalog.filter import TimestampFilter, AlwaysTrueFilter
from suricatalog.log import get_events_from_eve
from suricatalog.time import to_utc, parse_timestamp

BASEDIR = Path(__file__).parent


class SuricataLogTestCase(unittest.TestCase):
    """
    Unit test for suricata log common tests
    """
    eve_list = []
    old_date = datetime(
        year=2021,
        day=2,
        month=8,
        tzinfo=pytz.UTC
    )

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup data loading
        :return:
        """
        with open(BASEDIR.joinpath("eve.json"), 'rt', encoding='utf-8') as eve_file:
            for event in eve_file:
                SuricataLogTestCase.eve_list.append(json.loads(event))

    def test_to_utc(self):
        """
        Test UCT datetime handling
        :return:
        """
        naive = datetime.now()
        non_naive = datetime(
            year=2024,
            day=2,
            month=2,
            tzinfo=pytz.UTC
        )
        dates = [
            naive,
            non_naive
        ]
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
        invalid = 'XXX-02-08T16:32:14.900292'
        naive = datetime.now()
        non_naive = datetime(
            year=2024,
            day=2,
            month=2,
            tzinfo=pytz.UTC
        )
        dates = [
            '2022-02-08T16:32:14.900292+0000',
            '2022-02-08 16:32:14.900292+0000',
            '2022-02-08T16:32:14.900292',
            naive,
            non_naive,
            invalid
        ]
        for idx, test_date in enumerate(dates):
            try:
                ts = parse_timestamp(test_date)
                self.assertTrue(ts)
                self.assertIsInstance(ts, datetime)
                self.assertIsNotNone(ts.tzinfo)
            except ValueError:
                if idx == 6:
                    self.fail(f"Was supposed to fail with an invalid timestamp: {invalid}")
                else:
                    pass

    def test_timestamp_filter(self):
        """
        Test timestamp filtering
        :return:
        """
        timestamp_filter = TimestampFilter()
        timestamp_filter.timestamp = SuricataLogTestCase.old_date
        self.assertTrue(
            timestamp_filter.accept(data=SuricataLogTestCase.eve_list[0])
        )
        self.assertTrue(
            timestamp_filter.accept(data=SuricataLogTestCase.eve_list[132])
        )

    def test_get_alerts(self):
        """
        Test get alerts
        :return:
        """
        timestamp_filter = TimestampFilter()
        timestamp_filter.timestamp = SuricataLogTestCase.old_date
        all_alerts = [x for x in get_events_from_eve(
            eve_files=[BASEDIR.joinpath("eve.json")],
            data_filter=timestamp_filter
        ) if x['event_type'] == 'alert']
        self.assertIsNotNone(all_alerts)
        self.assertEqual(275, len(all_alerts))
        self.assertEqual('SURICATA Applayer Detect protocol only one direction', all_alerts[90]['alert']['signature'])

    def test_get_all_events(self):
        """
        Test get all event, unfiltered
        :return:
        """
        always_true_filter = AlwaysTrueFilter()
        all_events = list(get_events_from_eve(
            eve_files=[BASEDIR.joinpath("eve.json")],
            data_filter=always_true_filter
        ))
        self.assertIsNotNone(all_events)
        self.assertListEqual(SuricataLogTestCase.eve_list, all_events)


if __name__ == '__main__':
    unittest.main()
