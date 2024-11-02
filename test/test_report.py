"""
Unit test for reports
"""
import json
import unittest
from unittest import IsolatedAsyncioTestCase
from test.test_log import BASEDIR
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents


if __name__ == '__main__':
    unittest.main()


class ReportTestCase(IsolatedAsyncioTestCase):
    """
    Report test case
    """
    eve_list = []
    netflow_eve_list = []

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup data for testing
        :return:
        """
        with open(BASEDIR.joinpath("eve.json"), 'rt', encoding='utf-8') as eve_file:
            for event in eve_file:
                ReportTestCase.eve_list.append(json.loads(event))
        with open(BASEDIR.joinpath("eve_udp_flow.json"), 'rt', encoding='utf-8') as eve_file:
            for event in eve_file:
                ReportTestCase.netflow_eve_list.append(json.loads(event))

    async def test_aggregated_flow_proto_report(self):
        """
        Test flow report
        :return:
        """
        can_rep = AggregatedFlowProtoReport()
        for alert in ReportTestCase.eve_list:
            await can_rep.ingest_data(alert)
        self.assertIsNotNone(can_rep.port_proto_count)
        self.assertEqual(119, len(can_rep.port_proto_count.keys()))
        self.assertEqual(336, can_rep.port_proto_count[('TCP', 443)])

    async def test_host_data_use_report(self):
        """
        Test data use report
        :return:
        """
        hr = HostDataUseReport()
        for netflow_event in ReportTestCase.netflow_eve_list:
            await hr.ingest_data(netflow_event, '224.0.0.251')
        self.assertEqual(153339, hr.bytes)
        hr2 = HostDataUseReport()
        for netflow_event in ReportTestCase.netflow_eve_list:
            await hr2.ingest_data(netflow_event, '127.0.0.1')
            await hr.ingest_data(netflow_event, '127.0.0.1')
        self.assertEqual(0, hr2.bytes)
        self.assertEqual(153339, hr.bytes)

    async def test_top_user_agents(self):
        """
        Test top user agents
        :return:
        """
        tua = TopUserAgents()
        for event in ReportTestCase.eve_list:
            await tua.ingest_data(event)

        self.assertIsNotNone(tua.agents)
        self.assertTrue('test' in tua.agents)
        self.assertEqual(10, len(tua.agents))
