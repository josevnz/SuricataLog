import dataclasses
from typing import Dict, Any, Tuple


@dataclasses.dataclass
class AggregatedFlowProtoReport:
    port_proto_count: Dict[Tuple[str, int], int] = dataclasses.field(default_factory=dict)

    def ingest_data(self, data: Dict[Any, Any]) -> None:
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
    bytes: int = 0

    def ingest_data(self, data: Dict[Any, Any], dest: str) -> None:
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

    # TODO !!!!

    def ingest_data(self, data: Dict[Any, Any]) -> None:
        """
        cat eve.json | jq -s '[.[]|.http.http_user_agent]|group_by(.)|map({key:.[0],value:(.|length)})|from_entries'
        :param data:
        :return:
        """
        pass
