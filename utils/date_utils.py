"""Date utilities for parsing and formatting dates."""
from datetime import datetime


def parse_date(date_string: str) -> datetime:
    """Parse NEIS date string (YYYYMMDD) to datetime object."""
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:8])
    return datetime(year, month, day)


def format_date(date: datetime) -> str:
    """Format datetime object to YYYYMMDD string."""
    return date.strftime("%Y%m%d")