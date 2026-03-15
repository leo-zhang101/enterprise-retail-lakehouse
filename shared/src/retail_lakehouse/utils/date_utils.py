"""
Date and timezone utilities for the retail lakehouse platform.

Australia/Melbourne timezone handling for retail analytics.
"""

from datetime import date, datetime
from typing import Optional

from retail_lakehouse.config.constants import AUSTRALIA_MELBOURNE_TZ


def get_australia_now() -> datetime:
    """Return current datetime in Australia/Melbourne timezone."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(AUSTRALIA_MELBOURNE_TZ))
    except ImportError:
        try:
            import pytz
            return datetime.now(pytz.timezone(AUSTRALIA_MELBOURNE_TZ))
        except ImportError:
            return datetime.now()


def get_current_run_date() -> date:
    """Return the current run date in Australia/Melbourne (for partitioning)."""
    return get_australia_now().date()


def format_partition_path(base_path: str, partition_date: date) -> str:
    """
    Format a partition path: base_path/year=YYYY/month=MM/day=DD.

    Args:
        base_path: Base path (e.g. s3://bucket/entity or /data/raw/entity).
        partition_date: Date for the partition.

    Returns:
        Partitioned path string.
    """
    year = partition_date.strftime("%Y")
    month = partition_date.strftime("%m")
    day = partition_date.strftime("%d")
    path = base_path.rstrip("/")
    return f"{path}/year={year}/month={month}/day={day}"
