"""
Various utility functions that may be useful throughout heaobject.
"""
from datetime import datetime, timezone

def parse_bool(string: str) -> bool:
    """
    Returns a bool that is appropriate for the given input string. Strings such as "True", "true", "yes", "T", "y",
    and "Y" will return True, and strings such as "False", "false", "no", "t", "n", "N", and "" will return False. If
    string is not recognized, False will be returned.
    """
    return str(string).strip().lower() in ('true', 't', 'yes', 'y')


def now() -> datetime:
    """
    Returns the current datetime in UTC, with time zone information.

    :return: a datetime.
    """
    return datetime.now(timezone.utc)
