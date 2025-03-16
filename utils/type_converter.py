"""
Data type conversion utilities to handle common conversion issues.
This module helps standardize data type conversions throughout the application.
"""

from datetime import datetime, date
import numpy as np
import pandas as pd

def to_int(value):
    """
    Safely convert a value to Python int, handling None, numpy types, and strings.
    
    Args:
        value: Value to convert (can be int, numpy.int64, str, etc.)
        
    Returns:
        Python int or None if conversion is not possible
    """
    if value is None:
        return None
    
    try:
        # Handle numpy types with item() method
        if hasattr(value, 'item'):
            return int(value.item())
        # Handle string or regular int
        return int(value)
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None

def to_float(value):
    """
    Safely convert a value to Python float, handling None, numpy types, and strings.
    
    Args:
        value: Value to convert (can be float, numpy.float32, str, etc.)
        
    Returns:
        Python float or None if conversion is not possible
    """
    if value is None:
        return None
    
    try:
        # Handle numpy types with item() method
        if hasattr(value, 'item'):
            return float(value.item())
        # Handle string or regular float
        return float(value)
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None

def to_datetime(value):
    """
    Safely convert a value to Python datetime, handling None, pandas timestamps, and strings.
    
    Args:
        value: Value to convert (can be datetime, pandas.Timestamp, str, etc.)
        
    Returns:
        Python datetime or None if conversion is not possible
    """
    if value is None:
        return None
    
    try:
        # Handle pandas Timestamp
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        # Handle string
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        # Handle date
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, datetime.min.time())
        # Already datetime
        if isinstance(value, datetime):
            return value
        # Try generic conversion for other types
        return pd.to_datetime(value).to_pydatetime()
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None

def to_date(value):
    """
    Safely convert a value to Python date, handling None, pandas timestamps, and strings.
    
    Args:
        value: Value to convert (can be date, datetime, pandas.Timestamp, str, etc.)
        
    Returns:
        Python date or None if conversion is not possible
    """
    if value is None:
        return None
    
    try:
        # Handle datetime
        if isinstance(value, datetime):
            return value.date()
        # Handle pandas Timestamp
        if isinstance(value, pd.Timestamp):
            return value.date()
        # Handle string
        if isinstance(value, str):
            dt = pd.to_datetime(value)
            return dt.date()
        # Already date
        if isinstance(value, date):
            return value
        # Try generic conversion for other types
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None

def to_str(value):
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
        # Handle numpy types with item() method
        if hasattr(value, 'item'):
            return str(value.item())
        # Handle everything else
        return str(value)
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None