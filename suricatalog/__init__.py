"""
Package commons
"""
import locale
from pathlib import Path

locale.setlocale(locale.LC_ALL, '')
BASEDIR = Path(__file__).parent
DEFAULT_LOG_DIR = Path("/var/tmp")
