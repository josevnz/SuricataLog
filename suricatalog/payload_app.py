"""
Payload application
"""
from pathlib import Path
from typing import Type, List, Dict, Any

from textual import work
from textual.app import App, CSSPathType, ComposeResult
from textual.driver import Driver
from textual.widgets import LoadingIndicator

from suricatalog.filter import WithPayloadFilter, BaseFilter


class PayloadApp(App):
    """
    Base application for payload applications, shared logic
    """
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            eve: List[Path] = None,
            data_filter: WithPayloadFilter = None
    ):
        """
        Constructor
        :param driver_class:
        :param css_path:
        :param watch_css:
        :param eve:
        :param data_filter:
        """
        super().__init__(driver_class, css_path, watch_css)
        self.eve_files = None
        self.filter = None
        self.data_filter = data_filter
        self.eve = eve
        self.loaded = 0

    def set_filter(self, payload_filter: BaseFilter):
        """
        Set filter for application
        :param payload_filter:
        :return:
        """
        if not payload_filter:
            raise ValueError("Filter is required")
        self.filter = payload_filter

    def set_eve_files(self, eve_files: List[Path]):
        """
        Set eve files for application
        :param eve_files:
        :return:
        """
        if not eve_files:
            raise ValueError("One or more eve files is required")
        self.eve_files = eve_files

    def compose(self) -> ComposeResult:
        """
        Place TUI components
        :return:
        """
        yield LoadingIndicator()

    @work(exclusive=False)
    async def on_mount(self) -> None:
        """
        Initialize TUI components
        :return:
        """
        pass

    def action_quit_app(self) -> None:
        """
        Handle exit action
        :return:
        """
        self.exit("Exiting payload app now...")


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


def generate_filename(**payload_data: Dict[Any, any]):
    if 'payload_data' in payload_data:
        data = payload_data['payload_data']
    else:
        data = payload_data
    if not isinstance(data, dict):
        raise ValueError(f"payload_data must be a dict: {data}")
    timestamp = data.get("timestamp", None)
    if timestamp is None:
        raise ValueError(f"payload_data must have a timestamp: {data}")
    flow_id = data.get("flow_id", None)
    if flow_id is None:
        raise ValueError(f"payload_data must have a signature: {data}")
    dest_port = data.get("dest_port", "")
    src_ip = data.get("src_ip", "")
    dest_ip = data.get("dest_ip", "")
    src_port = data.get("src_port", "")
    filename = f"payload_export-{flow_id}-{timestamp}-{src_ip}:{src_port}-{dest_ip}:{dest_port}"
    return filename


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
    payload = alert['payload'] if 'payload' in alert else ""
    extracted = {
        "timestamp": timestamp,
        "dest_port": dest_port,
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "src_port": src_port,
        "payload": payload
    }
    return extracted

