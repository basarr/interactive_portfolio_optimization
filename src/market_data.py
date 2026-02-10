"""Optional historical data helpers (secondary to synthetic experiments)."""

from __future__ import annotations

import pandas as pd


def fetch_prices_yfinance(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Fetch adjusted close prices with yfinance.

    Raises
    ------
    ImportError
        If yfinance is not installed.
    """

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("Install yfinance to use fetch_prices_yfinance.") from exc

    data = yf.download(tickers=tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data.to_frame(name=tickers[0] if len(tickers) == 1 else "Close")
    return prices.dropna(how="all")


def compute_realized_vol(returns: pd.Series, window: int = 21, periods_per_year: int = 252) -> pd.Series:
    """Compute rolling annualized realized volatility from return series."""

    return returns.rolling(window=window).std() * (periods_per_year**0.5)
