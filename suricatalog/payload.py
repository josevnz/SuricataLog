from typing import Dict, Any, List


def get_key_from_map(map1: Dict[str, Any], keys: List[str]):
    """
    Return the first matching key from a map
    :param map1:
    :param keys:
    :return: Nothing ig none of the keys are in the map
    """
    val = ""
    for key in keys:
        if key in map1:
            val = map1[key]
            break
    return val


async def extract_from_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract alerts from event
    :param alert:
    :return:
    """
    timestamp = alert['timestamp']
    dest_port = str(get_key_from_map(alert, ['dest_port']))
    dest_ip = get_key_from_map(alert, ['dest_ip'])
    src_ip = get_key_from_map(alert, ['src_ip'])
    src_port = str(get_key_from_map(alert, ['src_port']))
    protocol = get_key_from_map(alert, ['app_proto', 'proto'])
    signature = alert['alert']['signature']
    payload = alert['payload'] if 'payload' in alert else ""
    return {
        "timestamp": timestamp,
        "dest_port": dest_port,
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "src_port": src_port,
        "protocol": protocol,
        "signature": signature,
        "payload": payload
    }
