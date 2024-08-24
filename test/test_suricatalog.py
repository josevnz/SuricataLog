import json
import unittest
from unittest import IsolatedAsyncioTestCase, TestCase
from datetime import datetime
from pathlib import Path

import pytz

from suricatalog.time import parse_timestamp, to_utc
from suricatalog.filter import NXDomainFilter, WithPrintablePayloadFilter, TimestampFilter, AlwaysTrueFilter
from suricatalog.log import get_events_from_eve
from suricatalog.report import AggregatedFlowProtoReport, HostDataUseReport, TopUserAgents

BASEDIR = Path(__file__).parent
events = []


class FilterTestCase(TestCase):

    def test_with_printable_payload_filter(self):
        data_filter = WithPrintablePayloadFilter()
        payload = json.loads('{"timestamp":"2022-02-08T16:32:14.900292+0000","flow_id":879564658970874,'
                             '"pcap_cnt":9146,"event_type":"alert","src_ip":"52.96.222.130","src_port":25,'
                             '"dest_ip":"10.2.8.102","dest_port":49880,"proto":"TCP","metadata":{"flowints":{'
                             '"applayer.anomaly.count":1}},"alert":{"action":"allowed","gid":1,'
                             '"signature_id":2260002,"rev":1,"signature":"SURICATA Applayer Detect protocol only one '
                             'direction","category":"Generic Protocol Command Decode","severity":3},"smtp":{"helo":"['
                             '173.166.146.112]"},"app_proto":"smtp","app_proto_tc":"failed",'
                             '"flow":{"pkts_toserver":3,"pkts_toclient":3,"bytes_toserver":198,"bytes_toclient":276,'
                             '"start":"2022-02-08T16:32:14.659706+0000"},"payload":"","payload_printable":"",'
                             '"stream":0,"packet":"AAgCHEevIOUqtpPxCABFAAAohfUAAIAGj5A0YN6CCgIIZgAZwth27Ik6+soFbVAQ'
                             '+vDMSAAA","packet_info":{"linktype":1},"host":"raspberrypi"}')
        self.assertFalse(data_filter.accept(payload))
        payload = json.loads('{"timestamp":"2022-02-08T16:32:20.491791+0000","flow_id":879564658970874,'
                             '"pcap_cnt":9254,"event_type":"alert","src_ip":"52.96.222.130","src_port":25,'
                             '"dest_ip":"10.2.8.102","dest_port":49880,"proto":"TCP","metadata":{"flowints":{'
                             '"applayer.anomaly.count":1,"smtp.anomaly.count":1}},"tx_id":0,'
                             '"alert":{"action":"allowed","gid":1,"signature_id":2220000,"rev":1,'
                             '"signature":"SURICATA SMTP invalid reply","category":"Generic Protocol Command Decode",'
                             '"severity":3},"smtp":{"helo":"[173.166.146.112]"},"app_proto":"smtp",'
                             '"app_proto_tc":"failed","flow":{"pkts_toserver":9,"pkts_toclient":14,'
                             '"bytes_toserver":570,"bytes_toclient":1148,"start":"2022-02-08T16:32:14.659706+0000"},'
                             '"payload":"TV0NCg==","payload_printable":"220 PH0P220CA0030.outlook.office365.com",'
                             '"stream":1,"packet":"AAgCH","packet_info":{"linktype":1},"host":"raspberrypi"}')
        self.assertTrue(data_filter.accept(payload))

    def test_with_printable_payload_filter_from_file(self):
        data_filter = WithPrintablePayloadFilter()
        # 84 of these payloads have a 'null',so they are expected to be filtered
        flow_ids = {
            1117051772115445,
            1117051772115445,
            879572199993573,
            1209610707920645,
            1101326487668301,
            248862673879386,
            248862673879386,
            1707519430412687,
            1707519430412687,
            879864496420835,
            1083777546714183,
            1357514933978659,
            879864496420835,
            206845708466045,
            653057280496748,
            232044371766299,
            833894710498356,
            833894710498356,
            667366924188955,
            94511204925000,
            41564274445680,
            277752553385435,
            806136472100536,
            611798819162769,
            749924187348801,
            1248865274295334,
            784224188217537,
            2132655805578936,
            2250553857023101,
            1980577284838437,
            1208016640841156,
            1980577284838437,
            1255871085730631,
            1296817044046536,
            1262262924962648,
            1211568756515917,
            636551925240335,
            657941680360877,
            644785005397810,
            249279597341217,
            201901383894597,
            242479979619734,
            394539153315441,
            244035746600868,
            278410102952556,
            685462364109190,
            1116734859441197,
            1116734859441197,
            1929642955916282,
            784369590587384,
            1911867894557238,
            1387833132456197,
            1616909837011682,
            1690259766491386,
            1616909837011682,
            1464936998127434,
            1579061810494998,
            1464936998127434,
            1579061810494998,
            2024483847095705,
            1692920326018047,
            2240848756896914,
            1684109579010675,
            1605766509821287,
            1736380214178990,
            1684109579010675,
            2198502421252463,
            2198502421252463,
            808114184483419,
            719606258986631,
            808114184483419,
            719606258986631,
            947551783206878,
            947551783206878,
            1431171568122864,
            382125840958721,
            382125840958721,
            2133828637592443,
            2109669390050495,
            2135326759364959,
            1913267474427766,
            1838515100344931,
            1915756617234611,
            1916415357571604,
            487984813931697,
            296466617085665,
            408302945206078,
            348636333008022,
            284724912486502,
            284724912486502,
            1655729925536716,
            733464559355118,
            348832191139035,
            1156650674014842,
            1640122311458474,
            356383397518687,
            1156650674014842,
            792788483047503,
            369725903275355,
            1105447458998123,
            1105447458998123,
            943516941319943,
            1303316325186687,
            644785005397810,
            97676645382088,
            296466617085665,
            2109669390050495,
            368053091258192,
            249279597341217,
            1395209664101095,
            667366924188955,
            2133828637592443,
            408302945206078,
            784369590587384,
            1690259766491386,
            348636333008022,
            242479979619734,
            1605766509821287
        }
        accepted_cnt = 34
        counted = 0
        with open(BASEDIR.joinpath("eve-2.json"), 'rt') as eve_file:
            for event in eve_file:
                payload = json.loads(event)
                accepted = data_filter.accept(payload)
                """
                Validation is tricky, as the payload is split across several alerts. For example:
                {"flow_id":1117051772115445,"payload":null,"alert":{"action":"allowed","gid":1,"signature_id":2260002,"rev":1,"signature":"SURICATA,
                ...
                {"flow_id":1117051772115445,"payload":"MjIwIHNtdHAubWFpbC55YWhvby5jb20gRVNNVFAgcmVhZHkNCjI1MC1rdWJlbm9kZTUxNS5tYWlsLXByb2QxLm9tZWdhLmdxMS55YWhvby5jb20gSGVsbG8gWzE3My4xNjYuMTQ2LjExMl0gWzE3My4xNjYuMTQ2LjExMl0pDQoyNTAtRU5IQU5DRURTVEFUVVNDT0RFUw0KMjUwLThCSVRNSU1FDQoyNTAtU0laRSA0MTY5NzI4MA0KMjUwIEFVVEggUExBSU4gTE9HSU4gWE9BVVRIMiBPQVVUSEJFQVJFUg0KMzM0IFZYTmxjbTVoYldVNg0KMzM0IFVHRnpjM2R2Y21RNg0KNTM1IDUuNy4wICgjQVVUSDAwNSkgVG9vIG1hbnkgYmFkIGF1dGggYXR0ZW1wdHMuDQo=","alert":{"action":"allowed","gid":1,"signature_id":2220000,"rev":1,"signature":"SURICATA,
                So we must manually ensure there is indeed a payload
                """
                if 'flow_id' in payload:
                    flow_id = payload['flow_id']
                    if flow_id in flow_ids:
                        if 'payload' in payload and not payload['payload'] == 'null':
                            self.assertTrue(accepted, payload)
                            counted += 1
                    else:
                        self.assertFalse(accepted, payload)
        self.assertEqual(accepted_cnt, counted)

    def test_nxdomain(self):
        data_filter = NXDomainFilter()
        payload = json.loads('{"timestamp":"2022-02-23T19:04:05.606882+0000","flow_id":1452066252079368,'
                             '"pcap_cnt":85538,"event_type":"dns","src_ip":"172.16.0.170","src_port":58529,'
                             '"dest_ip":"172.16.0.52","dest_port":53,"proto":"UDP","dns":{"version":2,"type":"answer",'
                             '"id":46693,"flags":"8583","qr":true,"aa":true,"rd":true,"ra":true,'
                             '"rrname":"wpad.sunnystation.com","rrtype":"A","rcode":"NXDOMAIN","authorities":[{'
                             '"rrname":"sunnystation.com","rrtype":"SOA","ttl":3600,'
                             '"soa":{"mname":"sunnystation-dc.sunnystation.com","rname":"hostmaster.sunnystation.com",'
                             '"serial":32,"refresh":900,"retry":600,"expire":86400,"minimum":3600}}]},'
                             '"host":"raspberrypi"}')
        self.assertTrue(data_filter.accept(payload))
        payload = json.loads('{"timestamp":"2022-02-08T15:08:22.266264+0000","flow_id":127219202876190,'
                             '"pcap_cnt":4196,"event_type":"tls","src_ip":"10.2.8.102","src_port":49798,'
                             '"dest_ip":"185.248.140.40","dest_port":443,"proto":"TCP","tls":{"subject":"C=GB, '
                             'ST=London, L=London, O=Global Security, OU=IT Department, CN=example.com",'
                             '"issuerdn":"C=GB, ST=London, L=London, O=Global Security, OU=IT Department, '
                             'CN=example.com","serial":"0E:B4:42:BB:46:DA:06:75:CF:4B:CA:7B:2B:E8:C2:60:0B:18:32:17",'
                             '"fingerprint":"28:c1:5a:60:d5:cb:a4:89:4b:07:c6:4c:d8:67:e7:f1:76:ef:da:aa",'
                             '"version":"TLS 1.2","notbefore":"2022-01-31T20:50:00","notafter":"2023-01-31T20:50:00",'
                             '"ja3":{"hash":"51c64c77e60f3980eea90869b68c58a8","string":"771,'
                             '49196-49195-49200-49199-49188-49187-49192-49191-49162-49161-49172-49171-157-156-61-60'
                             '-53-47-10,10-11-13-35-23-65281,29-23-24,0"},"ja3s":{'
                             '"hash":"ec74a5c51106f0419184d0dd08fb05bc","string":"771,49200,65281-11-35-23"}},'
                             '"host":"raspberrypi"}')
        self.assertFalse(data_filter.accept(payload))


class ReportTestCase(IsolatedAsyncioTestCase):
    eve_list = []
    netflow_eve_list = []

    @classmethod
    def setUpClass(cls) -> None:
        with open(BASEDIR.joinpath("eve.json"), 'rt') as eve_file:
            for event in eve_file:
                ReportTestCase.eve_list.append(json.loads(event))
        with open(BASEDIR.joinpath("eve_udp_flow.json"), 'rt') as eve_file:
            for event in eve_file:
                ReportTestCase.netflow_eve_list.append(json.loads(event))

    async def test_aggregated_flow_proto_report(self):
        events.append("test_aggregated_flow_proto_report")
        can_rep = AggregatedFlowProtoReport()
        for alert in ReportTestCase.eve_list:
            await can_rep.ingest_data(alert)
        self.assertIsNotNone(can_rep.port_proto_count)
        self.assertEqual(119, len(can_rep.port_proto_count.keys()))
        self.assertEqual(336, can_rep.port_proto_count[('TCP', 443)])

    async def test_host_data_use_report(self):
        events.append("test_host_data_use_report")
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
        events.append("test_top_user_agents")
        tua = TopUserAgents()
        for event in ReportTestCase.eve_list:
            await tua.ingest_data(event)

        self.assertIsNotNone(tua.agents)
        self.assertTrue('test' in tua.agents)
        self.assertEqual(10, len(tua.agents))


class SuricataLogTestCase(unittest.TestCase):
    eve_list = []
    old_date = datetime(
            year=2021,
            day=2,
            month=8,
            tzinfo=pytz.UTC
        )

    @classmethod
    def setUpClass(cls) -> None:
        with open(BASEDIR.joinpath("eve.json"), 'rt') as eve_file:
            for event in eve_file:
                SuricataLogTestCase.eve_list.append(json.loads(event))

    def test_to_utc(self):
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
        timestamp_filter = TimestampFilter()
        timestamp_filter._timestamp = SuricataLogTestCase.old_date
        self.assertTrue(
            timestamp_filter.accept(data=SuricataLogTestCase.eve_list[0])
        )
        self.assertTrue(
            timestamp_filter.accept(data=SuricataLogTestCase.eve_list[132])
        )

    def test_get_alerts(self):
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
        always_true_filter = AlwaysTrueFilter()
        all_events = [x for x in get_events_from_eve(
            eve_files=[BASEDIR.joinpath("eve.json")],
            data_filter=always_true_filter
        )]
        self.assertIsNotNone(all_events)
        self.assertListEqual(SuricataLogTestCase.eve_list, all_events)


if __name__ == '__main__':
    unittest.main()
