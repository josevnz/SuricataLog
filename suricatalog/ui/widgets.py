from timeit import default_timer as timer

SURICATALOG_HEADER_FOOTER_STYLE = "white on dark_blue"


def get_clock(start_time: float) -> str:
    seconds = timer() - start_time
    if seconds <= 60.0:
        return f"{seconds:.2f} secs"
    else:
        return f"{seconds/60.0:.2f} min"
