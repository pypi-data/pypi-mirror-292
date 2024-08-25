from datetime import datetime


def format_time(dt: datetime) -> str:
    return dt.astimezone().isoformat(timespec='seconds')