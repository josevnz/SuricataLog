from timeit import default_timer as timer

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Header, Footer

SURICATALOG_HEADER_FOOTER_STYLE = "white on dark_blue"


class EvelogAppHeader(Header):

    __start__time__ = timer()

    def get_clock(self) -> str:
        seconds = timer() - EvelogAppHeader.__start__time__
        if seconds <= 60.0:
            return f"{seconds:.2f} secs"
        else:
            return f"{seconds/60.0:.2f} min"

    def render(self) -> RenderableType:
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.style = self.style
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right", width=8)
        header_table.add_row(
            self.full_title, self.get_clock() if self.clock else ""
        )
        header: RenderableType
        header = Panel(header_table, style=self.style) if self.tall else header_table
        return header


class EvelogAppFooter(Footer):
    def make_key_text(self) -> Text:
        text = Text(
            style=SURICATALOG_HEADER_FOOTER_STYLE,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", "reverse" if hovered else "default on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text
