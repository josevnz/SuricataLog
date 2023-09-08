from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Union


class Formats(Enum):
    TABLE = "TABLE"
    JSON = "JSON"
    BRIEF = "BRIEF"

    def __str__(self):
        return self.name


def get_format(val: str) -> Union[Formats, None]:
    try:
        return Formats[val]
    except KeyError:
        return None


FORMATS = [fmt for fmt in Formats]


def load_css(the_file: Path):
    with open(the_file, 'r') as css_data:
        return "\n".join(css_data.readlines())
