"""
Collection of canned reports

"""
import dataclasses
from typing import Dict, Any, Tuple


@dataclasses.dataclass
class AggregatedFlowProtoReport:
    """
    FLow protocol report details
    """
    port_proto_count: Dict[Tuple[str, int], int] = dataclasses.field(default_factory=dict)

    async def ingest_data(self, data: Dict[Any, Any]) -> None:
        """
        ports=$(cat $PWD/test/eve.json|jq -c 'select(.event_type=="flow")|[.proto, .dest_port]'|sort |uniq -c)
        echo $ports
        1043 ["UDP",53]
        336 ["TCP",443]
        313 ["TCP",587]
        216 ["TCP",465]
        206 ["TCP",25]
        122 ["UDP",137]
        104 ["TCP",8080]
        70 ["TCP",88]
        61 ["TCP",80]
        59 ["TCP",389]

        To get only the top 10: echo $ports| sort -nr| head -n10
        :param data:
        :return:
        """
        if 'event_type' in data and 'flow' == data['event_type'] and 'dest_port' in data and 'proto' in data:
            port = data['dest_port'] if data['dest_port'] else ""
            proto_and_dest_port = (data['proto'], port)
            if proto_and_dest_port not in self.port_proto_count:
                self.port_proto_count[proto_and_dest_port] = 0
            self.port_proto_count[proto_and_dest_port] += 1


@dataclasses.dataclass
class HostDataUseReport:
    """
    Host data usage report
    """
    bytes: int = 0

    async def ingest_data(self, data: Dict[Any, Any], dest: str) -> None:
        """
        tail -n500000 /var/log/suricata/eve.json | \
        jq -s 'map(select(.event_type=="netflow" and .dest_ip=="224.0.0.251").netflow.bytes)|add'| /bin/numfmt --to=iec
        1.6M
        :param data:
        :param dest:
        :return:
        """
        if 'event_type' in data and 'netflow' == data['event_type'] and 'dest_ip' in data and dest == data['dest_ip']:
            self.bytes += data['netflow']['bytes']


class TopUserAgents:
    """
    Replicate tutorial top user agents query with jq.
    """

    agents: Dict[str, int] = {}

    async def ingest_data(self, data: Dict[Any, Any]) -> None:
        """
        cat eve.json | jq -s '[.[]|.http.http_user_agent]|group_by(.)|map({key:.[0],value:(.|length)})|from_entries'

        This particular rule is quite brittle, if data is incomplete you will get the following error:

        ```json
        jq: error (at <stdin>:14914): Cannot use null (null) as object key
        ```

        Instead of something like this:
        ```json
        {
            "Microsoft NCSI": 5,
            "Microsoft-CryptoAPI/6.1": 2,
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727;
            .NET CLR 3.0.30729; .NET CLR 3.5.30729)": 2,
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Win64; x64; Trident/7.0; .NET CLR 2.0.50727; SLCC2;
            .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)": 6,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko": 3,
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko": 2,
            "WinHTTP loader/1.0": 4,
            "WinHTTP sender/1.0": 2,
            "pwtyyEKzNtGatwnJjmCcBLbOveCVpc": 2,
            "test": 4
        }
        ```
        :param data:
        :return:
        """
        if 'event_type' in data and 'http' in data and 'http_user_agent' in data['http']:
            agent = data['http']['http_user_agent']
            if agent:
                if agent not in self.agents:
                    self.agents[agent] = 0
                self.agents[agent] += 1
