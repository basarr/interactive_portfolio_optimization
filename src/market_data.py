"""Optional historical data helpers (secondary to synthetic experiments)."""

from __future__ import annotations

import pandas as pd


def _extract_close_prices(data: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Extract close prices from possible yfinance output layouts."""

    if data.empty:
        return data

    if isinstance(data.columns, pd.MultiIndex):
        level0 = set(data.columns.get_level_values(0))
        if "Close" in level0:
            close = data["Close"]
        elif "Adj Close" in level0:
            close = data["Adj Close"]
        else:
            raise ValueError("Could not find 'Close' or 'Adj Close' in yfinance output.")
    else:
        if "Close" in data.columns:
            close = data[["Close"]]
        elif "Adj Close" in data.columns:
            close = data[["Adj Close"]]
        else:
            # Some yfinance layouts return a single unnamed column.
            close = data.iloc[:, [0]]

    if isinstance(close, pd.Series):
        close = close.to_frame(name=tickers[0])

    close = close.copy()
    if len(close.columns) == 1 and len(tickers) == 1:
        close.columns = [tickers[0]]
    return close


def fetch_prices_yfinance(
    tickers: list[str],
    start: str,
    end: str,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch adjusted close prices from Yahoo Finance.

    Parameters
    ----------
    tickers:
        Ticker list, e.g. ``[\"ASML\"]``.
    start, end:
        Date boundaries in ``YYYY-MM-DD`` format.
    interval:
        Yahoo interval string. Default is daily bars.
    """

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("Install yfinance to use fetch_prices_yfinance.") from exc

    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    prices = _extract_close_prices(data, tickers=tickers)
    prices.index = pd.to_datetime(prices.index)
    return prices.sort_index().dropna(how="all")


def price_gap_report(prices: pd.DataFrame, max_gap_days: int = 5) -> pd.DataFrame:
    """Return large calendar gaps between consecutive observations."""

    if prices.empty:
        return pd.DataFrame(columns=["prev_date", "next_date", "gap_days"])

    idx = pd.DatetimeIndex(prices.index).sort_values()
    diffs = idx.to_series().diff().dropna()
    out = pd.DataFrame(
        {
            "prev_date": idx[:-1].to_list(),
            "next_date": idx[1:].to_list(),
            "gap_days": diffs.dt.days.to_numpy(),
        }
    )
    return out[out["gap_days"] > max_gap_days].reset_index(drop=True)


def price_data_quality_report(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Build a concise data-integrity report for one ticker column."""

    series = prices[ticker].dropna() if ticker in prices.columns else pd.Series(dtype=float)
    first_date = series.index.min() if not series.empty else pd.NaT
    last_date = series.index.max() if not series.empty else pd.NaT
    max_gap = pd.DatetimeIndex(series.index).to_series().diff().dt.days.max() if len(series) > 1 else pd.NA

    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "n_obs": int(series.shape[0]),
                "first_date": first_date,
                "last_date": last_date,
                "has_missing_values": bool(prices[ticker].isna().any()) if ticker in prices.columns else True,
                "is_index_monotonic": bool(prices.index.is_monotonic_increasing),
                "has_duplicate_index": bool(prices.index.duplicated().any()),
                "max_calendar_gap_days": max_gap,
            }
        ]
    )


def assert_price_data_ready(
    prices: pd.DataFrame,
    ticker: str,
    start: str,
    min_obs: int = 252,
    max_gap_days: int = 5,
) -> None:
    """Validate historical price data before downstream quantitative analysis."""

    if prices.empty:
        raise ValueError("No price data returned.")
    if ticker not in prices.columns:
        raise ValueError(f"Ticker '{ticker}' not found in returned columns: {list(prices.columns)}")
    if prices.index.duplicated().any():
        raise ValueError("Price index contains duplicates.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("Price index must be monotonic increasing.")

    series = prices[ticker].dropna()
    if series.shape[0] < min_obs:
        raise ValueError(f"Insufficient observations: {series.shape[0]} < {min_obs}")

    start_ts = pd.Timestamp(start)
    first_date = series.index.min()
    if first_date > start_ts + pd.Timedelta(days=7):
        raise ValueError(f"Data starts too late. first_date={first_date.date()}, expected near {start}.")

    large_gaps = price_gap_report(prices[[ticker]], max_gap_days=max_gap_days)
    if not large_gaps.empty:
        raise ValueError(
            "Detected unexpected large calendar gaps. "
            f"First gap example: {large_gaps.iloc[0].to_dict()}"
        )


def compute_realized_vol(returns: pd.Series, window: int = 21, periods_per_year: int = 252) -> pd.Series:
    """Compute rolling annualized realized volatility from return series."""

    return returns.rolling(window=window).std() * (periods_per_year**0.5)
