"""Risk and performance metric utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cumulative_returns(returns: np.ndarray) -> np.ndarray:
    """Compute cumulative returns from simple return series."""

    arr = np.asarray(returns, dtype=float)
    return np.cumprod(1.0 + arr) - 1.0


def max_drawdown(returns: np.ndarray) -> float:
    """Compute maximum drawdown from simple return series."""

    arr = np.asarray(returns, dtype=float)
    wealth = np.cumprod(1.0 + arr)
    running_peak = np.maximum.accumulate(wealth)
    drawdowns = wealth / running_peak - 1.0
    return float(np.min(drawdowns))


def annualized_vol(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Annualized volatility of simple returns."""

    arr = np.asarray(returns, dtype=float)
    return float(np.std(arr, ddof=1) * np.sqrt(periods_per_year))


def cvar(values: np.ndarray, alpha: float = 0.05) -> float:
    """Compute lower-tail conditional value-at-risk at level alpha."""

    arr = np.asarray(values, dtype=float)
    cutoff = np.quantile(arr, alpha)
    tail = arr[arr <= cutoff]
    return float(np.mean(tail))


def summary_table(returns: np.ndarray, periods_per_year: int = 252) -> pd.DataFrame:
    """Return standard summary statistics for simple returns."""

    arr = np.asarray(returns, dtype=float)
    return pd.DataFrame(
        [
            {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr, ddof=1)),
                "annualized_vol": annualized_vol(arr, periods_per_year=periods_per_year),
                "cvar_95": cvar(arr, alpha=0.05),
                "max_drawdown": max_drawdown(arr),
            }
        ]
    )
