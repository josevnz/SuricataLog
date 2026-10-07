"""
Package commons
"""
import locale
from pathlib import Path
from typing import Any

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent
DEFAULT_LOG_DIR = Path("/var/tmp")


def get_key_from_map(data: dict[str, Any], keys: list[str]) -> str | None:
    """
    Return the first matching key from a map
    :param data: Dictionary to search
    :param keys: List of keys to try in order
    :return: First matching value or None if no key found
    """
    for key in keys:
        if key in data:
            return data[key]
    return None
