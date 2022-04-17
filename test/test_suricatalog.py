import unittest

from suricatalog import *

BASEDIR = Path(__file__).parent


class SuricataLogTestCase(unittest.TestCase):
    eve_list = []
    old_date = datetime.fromisoformat('2023-02-08T16:32:14.900292')

    @classmethod
    def setUpClass(cls) -> None:
        with open(BASEDIR.joinpath("eve.json"), 'rt') as eve_file:
            for event in eve_file:
                SuricataLogTestCase.eve_list.append(json.loads(event))

    def test_parse_timestamp(self):
        self.assertTrue(parse_timestamp('2022-02-08T16:32:14.900292+0000'))
        self.assertTrue(parse_timestamp('2022-02-08 16:32:14.900292+0000'))
        self.assertTrue(parse_timestamp('2022-02-08T16:32:14.900292'))
        try:
            parse_timestamp('XXX-02-08T16:32:14.900292')
            self.fail("Was supposed to fail with an invalid timestamp")
        except ValueError:
            pass

    def test_alert_filter(self):
        self.assertFalse(
            alert_filter(data=SuricataLogTestCase.eve_list[0], timestamp=SuricataLogTestCase.old_date)
        )
        self.assertTrue(
            alert_filter(data=SuricataLogTestCase.eve_list[132], timestamp=SuricataLogTestCase.old_date)
        )

    def test_get_alerts(self):
        all_alerts = [x for x in get_alerts_from_eve(
            timestamp=SuricataLogTestCase.old_date,
            eve_files=[BASEDIR.joinpath("eve.json")]
        )]
        self.assertIsNotNone(all_alerts)
        self.assertEqual(275, len(all_alerts))
        self.assertEqual('SURICATA Applayer Detect protocol only one direction', all_alerts[90]['alert']['signature'])


if __name__ == '__main__':
    unittest.main()
