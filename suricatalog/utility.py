from __future__ import annotations

from enum import Enum
from typing import Union


class Formats(Enum):
    TABLE = "TABLE"
    BRIEF = "BRIEF"

    def __str__(self):
        return self.name


def get_format(val: str) -> Union[Formats, None]:
    try:
        return Formats[val]
    except KeyError:
        return None


FORMATS = [fmt for fmt in Formats]
