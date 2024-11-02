"""
Discover code for table helpers
"""
from enum import Enum
from functools import partial
from typing import Any

from rich.style import Style
from textual.command import Provider, Hits, Hit, DiscoveryHit
from textual.screen import Screen
from textual.widgets import DataTable

from suricatalog.screens import DetailScreen


class TableColumns(Enum):
    """
    Columns for events
    """
    TIMESTAMP = 0
    SEVERITY = 1
    SIGNATURE = 2
    PROTOCOL = 3
    DESTINATION = 4
    SOURCE = 5
    PAYLOAD = 6


PROVIDER_COLS = [
    TableColumns.SIGNATURE,
    TableColumns.PROTOCOL,
    TableColumns.DESTINATION,
    TableColumns.SOURCE,
    TableColumns.PAYLOAD
]


class TableAlertProvider(Provider):
    """
    Event provider implementation
    """

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        """
        Constructor
        :param screen:
        :param match_style:
        """
        super().__init__(screen, match_style)
        self.alerts_tbl = None

    async def startup(self) -> None:
        """
        initialization for the provider, when firts loaded
        :return:
        """
        self.alerts_tbl = self.app.query(DataTable).first()

    async def discover(self) -> DiscoveryHit:
        """
        Value discovery
        :return:
        """
        my_app = self.screen.app
        for row_key in self.alerts_tbl.rows:
            row = self.alerts_tbl.get_row(row_key)
            my_app.log.info(f"Searching {row_key}:{row}")
            for column in PROVIDER_COLS:
                searchable = row[column.value]
                matcher = self.matcher(searchable)
                runner_detail = DetailScreen(data=row)
                yield DiscoveryHit(
                    display=matcher.highlight(f"{searchable}"),
                    text=f"{column.name}: {searchable}",
                    command=partial(my_app.push_screen, runner_detail),
                    help=f"Select by {column.name}"
                )
            break  # Only care about the first result

    async def search(self, query: str) -> Hits:
        """
        Value search
        :param query:
        :return:
        """
        matcher = self.matcher(query)
        my_app = self.screen.app
        for row_key in self.alerts_tbl.rows:
            row = self.alerts_tbl.get_row(row_key)
            my_app.log.info(f"Searching {row_key}:{row}")
            for column in PROVIDER_COLS:
                searchable = row[column.value]
                score = matcher.match(searchable)
                if score > 0:
                    runner_detail = DetailScreen(data=row)
                    yield Hit(
                        score=score,
                        match_display=matcher.highlight(f"{searchable}"),
                        command=partial(my_app.push_screen, runner_detail),
                        text=f"{column.name}: {searchable}",
                        help=f"Select by {column.name}"
                    )
