from enum import Enum
from functools import partial
from typing import Any

from rich.style import Style
from textual.command import Provider, Hits, Hit
from textual.screen import Screen
from textual.widgets import DataTable

from suricatalog.screens import DetailScreen


class TableColumns(Enum):
    Timestamp = 0
    Severity = 1
    Signature = 2
    Protocol = 3
    Destination = 4
    Source = 5
    Payload = 6


class TableAlertProvider(Provider):

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        self.alerts_tbl = None

    async def startup(self) -> None:
        self.alerts_tbl = self.app.query(DataTable).first()

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        my_app = self.screen.app
        for row_key in self.alerts_tbl.rows:
            row = self.alerts_tbl.get_row(row_key)
            my_app.log.info(f"Searching {row_key}:{row}")
            for column in [
                TableColumns.Signature,
                TableColumns.Protocol,
                TableColumns.Destination,
                TableColumns.Source,
                TableColumns.Payload
            ]:
                searchable = row[column.value]
                score = matcher.match(searchable)
                if score > 0:
                    runner_detail = DetailScreen(data=row)
                    yield Hit(
                        score,
                        matcher.highlight(f"{searchable}"),
                        partial(my_app.push_screen, runner_detail),
                        help=f"{column.name}: {searchable}"
                    )
