from datetime import timedelta, datetime, timezone, tzinfo
from typing import Union, Any
from timeit import default_timer as timer

import pytz

DEFAULT_TZ: tzinfo = datetime.now(timezone.utc).astimezone().tzinfo


def to_utc(candidate: datetime) -> datetime:
    try:
        converted = candidate.astimezone(pytz.utc)
    except (ValueError, TypeError):
        converted = candidate.replace(tzinfo=pytz.utc)
    return converted


DEFAULT_TIMESTAMP_10M_AGO: datetime = to_utc(datetime.now(tz=DEFAULT_TZ) - timedelta(minutes=10))
DEFAULT_TIMESTAMP_10Y_AGO: datetime = to_utc(datetime.now(tz=DEFAULT_TZ) - timedelta(days=365 * 10))


def parse_timestamp(candidate: Union[str, Any]) -> datetime:
    """
    Expected something like 2022-02-08T16:32:14.900292+0000
    :param candidate:
    :return:
    """
    if isinstance(candidate, str):
        try:
            iso_candidate = candidate.split('+', 1)[0]
            return to_utc(datetime.fromisoformat(iso_candidate))
        except ValueError:
            raise ValueError(f"Invalid date passed: {candidate}")
    else:
        return to_utc(candidate)


def get_clock(start_time: float) -> str:
    seconds = timer() - start_time
    if seconds <= 60.0:
        return f"{seconds:.2f} secs"
    else:
        return f"{seconds / 60.0:.2f} min"
