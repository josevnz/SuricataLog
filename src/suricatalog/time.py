"""
Common logic to handle timestamps and dates
"""
from datetime import UTC, datetime, timedelta, tzinfo
from timeit import default_timer as timer
from typing import Any

# Use built-in UTC instead of pytz for better performance
DEFAULT_TZ: tzinfo = datetime.now(UTC).astimezone().tzinfo


def to_utc(candidate: datetime) -> datetime:
    """
    Enable UTC for a given datetime
    :param candidate:
    :return:
    """
    if candidate.tzinfo is None:
        return candidate.replace(tzinfo=UTC)
    return candidate.astimezone(UTC)


DEFAULT_TIMESTAMP_10M_AGO: datetime = to_utc(datetime.now(tz=DEFAULT_TZ) - timedelta(minutes=10))
DEFAULT_TIMESTAMP_20M_AGO: datetime = to_utc(datetime.now(tz=DEFAULT_TZ) - timedelta(minutes=20))
DEFAULT_TIMESTAMP_10Y_AGO: datetime = to_utc(datetime.now(tz=DEFAULT_TZ) - timedelta(days=365 * 10))


def parse_timestamp(candidate: str | Any) -> datetime:
    """
    Expected something like 2022-02-08T16:32:14.900292+0000 or 2022-02-08T16:32:14.900292+00:00
    Python 3.11+ fromisoformat handles timezone offsets natively.
    :param candidate:
    :return:
    """
    if isinstance(candidate, str):
        try:
            # Python 3.11+ fromisoformat handles +0000 and +00:00 formats
            # For older Python versions, we normalize the timezone suffix
            if (candidate[-5] == '+' or candidate[-5] == '-') and candidate[-3] != ':':
                # Format like +0000 -> +00:00
                candidate = candidate[:-2] + ':' + candidate[-2:]
            return to_utc(datetime.fromisoformat(candidate))
        except ValueError as ex:
            raise ValueError(f"Invalid date passed: {candidate}") from ex
    else:
        return to_utc(candidate)


def get_clock(start_time: float) -> str:
    """
    Get the clock time from a timestamp, as pretty string
    :param start_time:
    :return:
    """
    seconds = timer() - start_time
    if seconds <= 60.0:
        return f"{seconds:.2f} secs"
    return f"{seconds / 60.0:.2f} min"
