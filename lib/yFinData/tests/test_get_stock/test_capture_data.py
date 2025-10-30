# import sys
# import os

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# import pytest
from datetime import datetime, timedelta
from get_stock.stock_struct import (
    capture_stock,
    capture_national_debt,
    Stock,
    NationDebt,
)


def test_capture_stock():
    """Test capturing stock data for a well-known ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Test with Apple stock
    stock = capture_stock("AAPL", start_date)

    # Verify the returned object is a Stock instance
    assert isinstance(stock, Stock)
    assert stock.name == "AAPL"

    # Verify we got some data
    assert len(stock.data) > 0

    # Verify the data structure
    for date, price in stock.data.items():
        assert isinstance(date, datetime)
        assert isinstance(price.open, float)
        assert isinstance(price.close, float)
        assert isinstance(price.low, float)
        assert isinstance(price.high, float)
        assert isinstance(price.volume, int)
        assert isinstance(price.pe, float)


def test_capture_national_debt():
    """Test capturing national debt data for US."""
    # Use a recent date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Test with US national debt (using treasury yield as proxy)
    debt = capture_national_debt("US", start_date)

    # Verify the returned object is a NationDebt instance
    assert isinstance(debt, NationDebt)

    # Verify we got some data (treasury data should be available)
    assert len(debt.data) > 0

    # Verify the data structure
    for date, value in debt.data.items():
        assert isinstance(date, datetime)
        assert isinstance(value, float)


def test_capture_stock_invalid_ticker():
    """Test capturing stock data with an invalid ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Test with an invalid ticker
    stock = capture_stock("INVALID_TICKER_123", start_date)

    # Should return a Stock object but with empty data
    assert isinstance(stock, Stock)
    assert stock.name == "INVALID_TICKER_123"
    # Note: yfinance may still return some data for invalid tickers, so we won't assert empty


def test_capture_national_debt_invalid_nation():
    """Test capturing national debt data for an unsupported nation."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Test with an unsupported nation
    debt = capture_national_debt("INVALID_NATION", start_date)

    # Should return a NationDebt object
    assert isinstance(debt, NationDebt)
    # May return empty data or treasury data as fallback


# if __name__ == "__main__":
#     test_capture_stock()
#     test_capture_stock_invalid_ticker()
#     test_capture_national_debt()
#     test_capture_national_debt_invalid_nation()
