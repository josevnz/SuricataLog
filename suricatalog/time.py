from datetime import timedelta, datetime
from typing import Union, Any
from timeit import default_timer as timer

DEFAULT_TIMESTAMP_10M_AGO = datetime = datetime.now() - timedelta(minutes=10)
DEFAULT_TIMESTAMP_10Y_AGO = datetime = datetime.now() - timedelta(days=365 * 10)


def parse_timestamp(candidate: Union[str, Any]) -> datetime:
    """
    Expected something like 2022-02-08T16:32:14.900292+0000
    :param candidate:
    :return:
    """
    if isinstance(candidate, str):
        try:
            iso_candidate = candidate.split('+', 1)[0]
            return datetime.fromisoformat(iso_candidate)
        except ValueError:
            raise ValueError(f"Invalid date passed: {candidate}")
    elif isinstance(candidate, datetime):
        return candidate
    else:
        raise ValueError(f"I don't know how to handle {candidate}")


def get_clock(start_time: float) -> str:
    seconds = timer() - start_time
    if seconds <= 60.0:
        return f"{seconds:.2f} secs"
    else:
        return f"{seconds / 60.0:.2f} min"
