"""
Unit tests for clipboard data copy
"""
import unittest
from typing import List

from textual.widgets import Digits, RichLog, DataTable
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from suricatalog.clipboard import copy_from_digits, copy_from_richlog, copy_from_table


class ClipboardRichLogDemoApp(App):
    """
    Test application to copy data from rich log
    """
    BINDINGS = [
        ("c", "copy", "Copy to clipboard")
    ]

    def __init__(
            self,
            log_update: str
    ):
        """
        Constructor
        :param log_update:
        """
        super().__init__()
        self.copied = None
        self.ln = -1
        self.update = log_update

    def compose(self) -> ComposeResult:
        """
        Compose items for the TUI
        :return:
        """
        yield Header()
        log = RichLog()
        log.write(self.update)
        log.write(self.update)
        yield log
        yield Footer()

    def action_copy(self):
        """
        Copy data to the clipboard
        :return:
        """
        log = self.query_one(RichLog)
        (self.copied, self.ln) = copy_from_richlog(log)


class ClipboardDataTableDemoApp(App):
    """
    Demo application to copy data from data table
    """
    BINDINGS = [
        ("c", "copy", "Copy to clipboard")
    ]

    def __init__(
            self,
            table_update: List[List[str]]
    ):
        """
        Constructor
        :param table_update:
        """
        super().__init__()
        self.copied = None
        self.ln = -1
        self.update = table_update

    def compose(self) -> ComposeResult:
        """
        Compose TUI elements
        :return:
        """
        yield Header()
        table = DataTable()
        table.add_columns(*self.update[0])
        table.add_rows(self.update[1:])
        yield table
        yield Footer()

    def action_copy(self):
        """
        Override action to copy data from data table
        :return:
        """
        table = self.query_one(DataTable)
        (self.copied, self.ln) = copy_from_table(table)


class ClipboardTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Test cases for clipboard data copy
    """
    def test_copy_from_digits(self):
        """
        Copy digits
        :return:
        """
        digits = Digits()
        update = "Got a gazzillion bytes!"
        digits.update(update)
        copied, ln = copy_from_digits(digits)
        self.assertEqual(update, copied)
        self.assertEqual(23, ln)

    async def test_copy_from_richlog(self):
        """
        Copy rich log
        :return:
        """
        update = "Got 1973!"
        app = ClipboardRichLogDemoApp(log_update=update)
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")  # Copy to clipboard
            await pilot.pause()
        self.assertEqual('Got 1973!\nGot 1973!', app.copied)
        self.assertEqual(19, app.ln)

    async def test_copy_from_table(self):
        """
        Copy data from table
        :return:
        """
        update = [
            ['Login ID', 'Full Name'],
            ["1973", "Jose Vicente Nunez"],
            ["1973", "Jose Vicente Nunez"]
        ]
        app = ClipboardDataTableDemoApp(table_update=update)
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")  # Copy to clipboard
            await pilot.pause()
        self.assertEqual(86, app.ln)


if __name__ == '__main__':
    unittest.main()
