from datetime import datetime, timezone


def format_datetime(value, fmt):
    return value.strftime(fmt)


def format_timestamp(value, fmt=None):
    rv = datetime.fromtimestamp(value, timezone.utc)
    if fmt:
        return rv.strftime(fmt)
    return rv
