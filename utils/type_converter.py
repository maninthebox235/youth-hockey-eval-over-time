"""
Data type conversion utilities to handle common conversion issues.
This module helps standardize data type conversions throughout the application.
"""

from typing import Any, Optional
from datetime import datetime, date


def to_int(value: Any) -> Optional[int]:
    """
    Safely convert a value to Python int, handling None, numpy types, and strings.

    Args:
        value: Value to convert (can be int, numpy.int64, str, etc.)

    Returns:
        Python int or None if conversion is not possible
    """
    if value is None:
        return None

    # Handle numpy types that have .item() method (numpy.int64, numpy.int32, etc.)
    if hasattr(value, "item"):
        try:
            # This converts numpy types to native Python types
            return int(value.item())
        except (ValueError, TypeError, AttributeError):
            pass

    # Try direct conversion
    try:
        # Force to Python native int for compatibility with database drivers
        return int(value)
    except (ValueError, TypeError):
        return None

    # The returned value is guaranteed to be a native Python int
    # This ensures compatibility with database drivers like psycopg2
    # which may not handle numpy numeric types directly


def to_float(value: Any) -> Optional[float]:
    """
    Safely convert a value to Python float, handling None, numpy types, and strings.

    Args:
        value: Value to convert (can be float, numpy.float32, str, etc.)

    Returns:
        Python float or None if conversion is not possible
    """
    if value is None:
        return None

    # Handle numpy types that have .item() method (numpy.float32, numpy.float64, etc.)
    if hasattr(value, "item"):
        try:
            # This converts numpy types to native Python types
            return float(value.item())
        except (ValueError, TypeError, AttributeError):
            pass

    # Try direct conversion
    try:
        # Force to Python native float for compatibility with database drivers
        return float(value)
    except (ValueError, TypeError):
        return None

    # The returned value is guaranteed to be a native Python float
    # This ensures compatibility with database drivers like psycopg2
    # which may not handle numpy numeric types directly


def to_datetime(value: Any) -> Optional[datetime]:
    """
    Safely convert a value to Python datetime, handling None, pandas timestamps, and strings.

    Args:
        value: Value to convert (can be datetime, pandas.Timestamp, str, etc.)

    Returns:
        Python datetime or None if conversion is not possible
    """

    if value is None:
        return None

    # Already a datetime object
    if isinstance(value, datetime):
        return value

    # Handle pandas Timestamp
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime()
        except (ValueError, TypeError, AttributeError):
            pass

    # Try parsing string
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except (ValueError, TypeError):
                    return None

    return None


def to_date(value: Any) -> Optional[date]:
    """
    Safely convert a value to Python date, handling None, pandas timestamps, and strings.

    Args:
        value: Value to convert (can be date, datetime, pandas.Timestamp, str, etc.)

    Returns:
        Python date or None if conversion is not possible
    """

    if value is None:
        return None

    # Already a date object
    if isinstance(value, date):
        if isinstance(value, datetime):
            return value.date()
        return value

    # Handle pandas Timestamp
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime().date()
        except (ValueError, TypeError, AttributeError):
            pass

    # Convert from datetime
    if isinstance(value, datetime):
        return value.date()

    # Try parsing string
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except (ValueError, TypeError):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None

    return None


def to_str(value: Any) -> Optional[str]:
    """
    Safely convert a value to Python string, handling None and all other types.

    Args:
        value: Value to convert

    Returns:
        Python string or None if value is None
    """
    if value is None:
        return None

    try:
        return str(value)
    except (ValueError, TypeError):
        return None
