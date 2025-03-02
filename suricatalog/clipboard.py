"""
Common logic to handle copying data to the clipboard.
Depending on how much data you are displaying, these may can crash the application.
"""
from typing import Tuple, Any

import pyperclip
from textual.widgets import RichLog, DataTable, Digits
import orjson


def copy_from_richlog(rich_log: RichLog) -> Tuple[str, int]:
    """
    Extract data from rich log.
    Messages are not properly formatted as JSON, they are copied 'as-is'
    :param rich_log:
    :return:
    """
    if rich_log is None:
        return "", 0
    text_to_copy = '\n'.join([strip.text.strip() for strip in rich_log.lines])
    pyperclip.copy(text_to_copy)
    return text_to_copy, len(text_to_copy)


def copy_from_digits(digits: Digits) -> Tuple[str, int]:
    """
    Extract data from digits
    :param digits:
    :return:
    """
    if digits is None:
        return "", 0
    text_to_copy = digits.value
    pyperclip.copy(text_to_copy)
    return text_to_copy, len(text_to_copy)


def copy_from_table(data_table: DataTable) -> tuple[list[Any], int] | tuple[str, int]:
    """
    Extract data from table
    :param data_table:
    :return:
    """
    if data_table is None:
        return [], 0
    rows = []
    columns = []
    for key, column in data_table.columns.items():
        columns.append(column.label.plain)
    rows.append(columns)
    for key in data_table.rows:
        row = data_table.get_row(key)
        rows.append(row)
    text_to_copy = orjson.dumps(rows, option=orjson.OPT_SORT_KEYS).decode('utf-8')
    pyperclip.copy(text_to_copy)
    return text_to_copy, len(text_to_copy)
