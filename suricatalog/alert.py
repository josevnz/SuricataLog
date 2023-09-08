import locale
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, ListView, Header

from suricatalog.utility import load_css

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent


class JsonAlert(App):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]

    CSS_FILE = BASEDIR.joinpath('css').joinpath('alert.css')
    CSS = load_css(CSS_FILE)

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView()
        yield Footer()

    def on_mount(self) -> None:
        list_view = self.query_one(ListView)

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")


class TableAlert(App):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")


class BriefAlert(App):
    BINDINGS = [
        ("q", "quit_app", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_quit_app(self) -> None:
        self.exit("Exiting Alerts now...")
