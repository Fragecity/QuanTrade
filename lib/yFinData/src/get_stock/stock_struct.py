from dataclasses import dataclass
from math import isnan

from typing import Optional, Dict, List
from datetime import datetime
import yfinance as yf
from constants import TREASURY_SYMBOLS


@dataclass
class Price:
    open: float
    close: float
    low: float
    high: float
    volume: int
    pe: float


@dataclass
class Stock:
    name: str
    data: Dict[datetime, Price]
    tags: Optional[List[str]]


@dataclass
class NationDebt:
    data: Dict[datetime, float]


def capture_stock(name: str, start: datetime) -> Stock:
    """
    Capture stock data using yfinance.

    Args:
        name: Stock ticker symbol (e.g., 'AAPL')
        start: Start date for data retrieval
        end: End date for data retrieval
        period: Period string for yfinance (e.g., '1d', '1mo', '1y')

    Returns:
        Stock object with historical price data
    """
    start_str = start.strftime("%Y-%m-%d")
    end = datetime.now()
    end_str = end.strftime("%Y-%m-%d")

    ticker = yf.Ticker(name)
    hist = ticker.history(start=start_str, end=end_str)

    # Get P/E ratio from info
    pe_ratio = ticker.info.get("trailingPE")
    if pe_ratio is None or not isinstance(pe_ratio, (int, float)):
        pe_ratio = float("nan")
    else:
        pe_ratio = float(pe_ratio)

    # Build price data dictionary
    price_data: Dict[datetime, Price] = {}
    for date, row in hist.iterrows():
        # Convert pandas timestamp to datetime
        dt = date.to_pydatetime()
        price = Price(
            open=float(row["Open"]),
            close=float(row["Close"]),
            low=float(row["Low"]),
            high=float(row["High"]),
            volume=int(row["Volume"]),
            pe=pe_ratio,
        )
        price_data[dt] = price

    return Stock(name=name, data=price_data, tags=None)


def capture_national_debt(nation: str, start: datetime) -> NationDebt:
    """
    Capture national debt data. Note: yfinance doesn't directly provide national debt data,
    so this function uses treasury bond data as a proxy or returns empty data.

    Args:
        nation: Nation identifier (e.g., 'US' for United States)
        start: Start date for data retrieval
        end: End date for data retrieval

    Returns:
        NationDebt object with debt data (proxied by treasury yields)
    """
    # For national debt, we use treasury bond data as a proxy
    # Common treasury symbols: ^TNX (10-year yield), ^IRX (3-month yield)
    symbol = TREASURY_SYMBOLS.get(nation, "^TNX")

    start_str = start.strftime("%Y-%m-%d")
    end = datetime.now()
    end_str = end.strftime("%Y-%m-%d")

    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_str, end=end_str)

    debt_data = {}
    for date, row in hist.iterrows():
        dt = date.to_pydatetime()
        # Use closing yield as proxy for debt level
        debt_data[dt] = float(row["Close"])

    return NationDebt(data=debt_data)
