"""
Payload application
"""
import base64
import re
import traceback
from pathlib import Path
from typing import Any

from textual import on, work
from textual.app import App, ComposeResult, CSSPathType
from textual.containers import Center, Middle
from textual.driver import Driver
from textual.widgets import DataTable, Footer, Header, ProgressBar
from textual.worker import get_current_worker

from suricatalog.filter import WithPayloadFilter
from suricatalog.log import EveLogHandler


class PayloadApp(App):
    """
    Base application for payload applications, shared logic
    No clipboard binding here as it makes no sense.
    """
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]
    ENABLE_COMMAND_PALETTE = False
    current_sorts: set = set()

    def __init__(
            self,
            driver_class: type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            eve: list[Path] = None,
            data_filter: WithPayloadFilter = None,
            report_dir: Path = None,
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
        if not eve:
            raise ValueError("At least one Eve file is required")
        self.eve = eve
        if not data_filter:
            data_filter = WithPayloadFilter()
        self.data_filter = data_filter
        if not report_dir:
            raise ValueError("Destination report is missing")
        self.report_dir = report_dir
        self.loaded = 0

    @staticmethod
    def get_key_from_map(map1: dict[str, Any], keys: list[str]):
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

    @staticmethod
    def convert_to_filename(orig: str | None) -> str:
        """
        Make sure string is safe with filesystem
        :param orig:
        :return:
        """
        if orig is None:
            return "no_signature"
        filename = re.sub(r'\W+', '', orig)
        filename = filename.replace(' ', '_')
        return filename

    @staticmethod
    def generate_filename(
            base_dir: Path,
            prefix: str = "payload_export",
            **payload_data: dict[Any, Any],
    ) -> Path:
        """
        Generate a filename from payload components
        :param base_dir
        :param prefix:
        :param payload_data:
        :return:
        """
        data = payload_data.get('payload_data', payload_data)
        if not isinstance(data, dict):
            raise ValueError(f"payload_data must be a dict: {data}")
        timestamp = data.get("timestamp", None)
        if timestamp is None:
            raise ValueError(f"payload_data must have a timestamp: {data}")
        signature = data.get("signature", None)
        if signature is None:
            raise ValueError(f"payload_data must have a signature: {data}")
        signature = PayloadApp.convert_to_filename(signature)
        dest_port = data.get("dest_port", "")
        src_ip = data.get("src_ip", "")
        dest_ip = data.get("dest_ip", "")
        src_port = data.get("src_port", "")
        filename = f"{prefix}-{signature}-{timestamp}-{src_ip}:{src_port}-{dest_ip}:{dest_port}"
        return base_dir / filename

    @staticmethod
    async def extract_from_alert(
            alert: dict[str, Any]
    ) -> None | dict[str, Any]:
        """
        Extract alerts from event. Handle version changes between Suricata 6 and 7+.
        :param alert:
        :return:
        """
        if 'payload' not in alert:
            return None
        try:
            timestamp = alert['timestamp']
            dest_port = str(PayloadApp.get_key_from_map(alert, ['dest_port']))
            dest_ip = PayloadApp.get_key_from_map(alert, ['dest_ip'])
            src_ip = PayloadApp.get_key_from_map(alert, ['src_ip'])
            src_port = str(PayloadApp.get_key_from_map(alert, ['src_port']))
            payload = alert['payload']
            if 'signature' in alert:
                signature = alert['signature']
            else:
                signature = alert['alert']['signature']
            extracted = {
                "timestamp": timestamp,
                "dest_port": dest_port,
                "src_ip": src_ip,
                "dest_ip": dest_ip,
                "src_port": src_port,
                "payload": payload,
                "signature": signature
            }
            return extracted
        except KeyError as ke:
            raise KeyError(f"alert={alert}", ke) from ke

    def compose(self) -> ComposeResult:
        """
        Place TUI components
        :return:
        """
        yield Header()
        with Center(), Middle():
            yield ProgressBar(total=100, show_eta=False)
        yield Footer()

    async def on_mount(self) -> None:
        """
        Initialize TUI components
        :return:
        """
        self.pump_events()
        if self.loaded > 0:
            self.notify(
                title="Finished extracting payloads from events",
                severity="information",
                timeout=5,
                message=f"Number of payload exported: {self.loaded}"
            )

    def action_quit_app(self) -> None:
        """
        Handle exit action
        :return:
        """
        self.exit("Exiting payload app now...")

    @staticmethod
    async def save_payload(payload: dict[str, Any], payload_file: Path) -> int:
        """
        Save the extracted payload to disk
        :param payload:
        :param payload_file:
        :return: Length of the payload saved
        """
        with open(payload_file, "wb") as payload_fh:
            try:
                bin_payload = base64.b64decode(payload['payload'], altchars=None, validate=False)
                payload_fh.write(bin_payload)
                payload_fh.flush()
                return len(payload['payload'])
            except (TypeError, ValueError):
                payload_fh.write(payload['payload'])
                payload_fh.flush()
                return len(payload['payload'])

    def sort_reverse(self, sort_type: str):
        """
        Determine if `sort_type` is ascending or descending.
        :param sort_type: Keep track of column being sorted.
        """
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        """
        Handle clicks on table header
        :param event:
        :return:
        """
        eve_files_tbl: DataTable = event.data_table
        eve_files_tbl.sort(
            event.column_key,
            reverse=self.sort_reverse(event.column_key.value)
        )

    @staticmethod
    def unique_id(extracted: dict[Any, Any]) -> str:
        """
        Get the unique id based on extracted payload components
        :param extracted:
        :return:
        """
        if 'signature' not in extracted:
            raise ValueError("Missing signature")
        if 'timestamp' not in extracted:
            raise ValueError("Missing timestamp")
        uid = extracted['signature'] + str(extracted['timestamp'])
        return uid

    @work(exclusive=True, thread=True)
    async def pump_events(self):
        """
        Get events from eve log and send them to the application log
        :param
        :return:
        """
        try:
            worker = get_current_worker()
            extract_ids = set([])
            # Need to count the events first. And don't want to store them in memory because the payload may be
            # huge...
            eve_lh = EveLogHandler()
            for alert_with_payload in eve_lh.get_events(eve_files=self.eve, data_filter=self.data_filter):
                extracted = await PayloadApp.extract_from_alert(alert=alert_with_payload)
                uid = self.unique_id(extracted=extracted)
                extract_ids.add(uid)
            progress_bar = self.query_one(ProgressBar)
            if extract_ids:
                self.loaded = 1
                for alert_with_payload in eve_lh.get_events(eve_files=self.eve, data_filter=self.data_filter):
                    extracted = await PayloadApp.extract_from_alert(alert=alert_with_payload)
                    file_name = PayloadApp.generate_filename(
                        base_dir=self.report_dir,
                        payload_data=extracted
                    )
                    await self.save_payload(payload_file=file_name, payload=extracted)
                    progress = (self.loaded / len(extract_ids)) * 100.0
                    if not worker.is_cancelled:
                        self.call_from_thread(
                            progress_bar.update,
                            total=len(extract_ids),
                            progress=progress
                        )
                        self.loaded += 1
            else:
                if not worker.is_cancelled:
                    self.call_from_thread(
                        self.notify,
                        message="There are no payloads to extract!",
                        timeout=30,
                        title="Provided files do not have a single payload.",
                        severity="warning"
                    )
                    progress = 100.0
                    self.call_from_thread(
                        progress_bar.update,
                        total=len(extract_ids),
                        progress=progress
                    )

        except ValueError as ve:
            if hasattr(ve, 'message'):
                reason = ve.message
            elif hasattr(ve, 'reason'):
                reason = f"{ve}"
            else:
                reason = f"{ve}"
            tb = traceback.extract_stack()
            self.notify(
                message=f"{reason}. {tb}",
                timeout=20,
                title="There was a problem extracting the payloads",
                severity="error"
            )
            raise ValueError("There was a problem extracting the payloads", ve) from ve
