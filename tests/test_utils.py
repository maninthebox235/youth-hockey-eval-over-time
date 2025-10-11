"""Tests for utility functions."""

import numpy as np
import pandas as pd
from datetime import datetime, date
from utils.type_converter import to_int, to_float, to_datetime, to_date, to_str


class TestTypeConverter:
    """Tests for type conversion utilities."""

    def test_to_int_with_python_int(self):
        """Test to_int with Python int."""
        assert to_int(5) == 5
        assert to_int(0) == 0
        assert to_int(-10) == -10

    def test_to_int_with_numpy_int(self):
        """Test to_int with NumPy int types."""
        assert to_int(np.int64(42)) == 42
        assert to_int(np.int32(100)) == 100

    def test_to_int_with_string(self):
        """Test to_int with string."""
        assert to_int("123") == 123
        assert to_int("-45") == -45

    def test_to_int_with_none(self):
        """Test to_int with None."""
        assert to_int(None) is None

    def test_to_int_with_invalid(self):
        """Test to_int with invalid input."""
        assert to_int("invalid") is None
        assert to_int([1, 2, 3]) is None

    def test_to_float_with_python_float(self):
        """Test to_float with Python float."""
        assert to_float(3.14) == 3.14
        assert to_float(0.0) == 0.0
        assert to_float(-2.5) == -2.5

    def test_to_float_with_numpy_float(self):
        """Test to_float with NumPy float types."""
        assert to_float(np.float64(3.14)) == 3.14
        assert to_float(np.float32(2.5)) == 2.5

    def test_to_float_with_string(self):
        """Test to_float with string."""
        assert to_float("3.14") == 3.14
        assert to_float("-2.5") == -2.5

    def test_to_float_with_none(self):
        """Test to_float with None."""
        assert to_float(None) is None

    def test_to_datetime_with_python_datetime(self):
        """Test to_datetime with Python datetime."""
        dt = datetime(2024, 1, 15, 10, 30)
        assert to_datetime(dt) == dt

    def test_to_datetime_with_pandas_timestamp(self):
        """Test to_datetime with pandas Timestamp."""
        ts = pd.Timestamp("2024-01-15 10:30:00")
        result = to_datetime(ts)
        assert isinstance(result, datetime)

    def test_to_datetime_with_string(self):
        """Test to_datetime with string."""
        result = to_datetime("2024-01-15 10:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_to_datetime_with_none(self):
        """Test to_datetime with None."""
        assert to_datetime(None) is None

    def test_to_date_with_python_date(self):
        """Test to_date with Python date."""
        d = date(2024, 1, 15)
        assert to_date(d) == d

    def test_to_date_with_datetime(self):
        """Test to_date with datetime."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = to_date(dt)
        assert result == date(2024, 1, 15)

    def test_to_date_with_string(self):
        """Test to_date with string."""
        result = to_date("2024-01-15")
        assert isinstance(result, date)
        assert result.year == 2024

    def test_to_date_with_none(self):
        """Test to_date with None."""
        assert to_date(None) is None

    def test_to_str_with_various_types(self):
        """Test to_str with various types."""
        assert to_str("hello") == "hello"
        assert to_str(123) == "123"
        assert to_str(3.14) == "3.14"
        assert to_str(True) == "True"

    def test_to_str_with_none(self):
        """Test to_str with None."""
        assert to_str(None) is None
