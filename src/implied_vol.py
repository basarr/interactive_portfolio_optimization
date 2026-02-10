"""Implied volatility inversion utilities."""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
import pandas as pd

from .black_scholes import bs_price, bs_vega


Method = Literal["hybrid", "bisection"]


def _no_arbitrage_bounds(S: float, K: float, r: float, q: float, T: float, option_type: str) -> tuple[float, float]:
    disc_spot = S * math.exp(-q * T)
    disc_strike = K * math.exp(-r * T)
    if option_type.lower() == "call":
        lower = max(0.0, disc_spot - disc_strike)
        upper = disc_spot
    elif option_type.lower() == "put":
        lower = max(0.0, disc_strike - disc_spot)
        upper = disc_strike
    else:
        raise ValueError("option_type must be 'call' or 'put'.")
    return lower, upper


def implied_vol(
    price: float,
    S: float,
    K: float,
    r: float,
    q: float,
    T: float,
    option_type: str,
    method: Method = "hybrid",
    lower: float = 1e-6,
    upper: float = 5.0,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> float:
    """Invert Black-Scholes price to implied volatility.

    Parameters
    ----------
    price : float
        Observed option premium.
    S, K, r, q, T : float
        Standard Black-Scholes inputs with continuous rates.
    option_type : str
        Either ``"call"`` or ``"put"``.
    method : {"hybrid", "bisection"}
        Hybrid uses Newton step when safe and falls back to bisection.
    """

    if price <= 0:
        raise ValueError("Option price must be positive for implied volatility inversion.")

    low_bound, high_bound = _no_arbitrage_bounds(S, K, r, q, T, option_type)
    if not (low_bound - tol <= price <= high_bound + tol):
        raise ValueError(
            f"Price={price:.6f} violates no-arbitrage bounds [{low_bound:.6f}, {high_bound:.6f}]"
        )

    low = lower
    high = upper
    f_low = bs_price(S, K, r, q, low, T, option_type) - price
    f_high = bs_price(S, K, r, q, high, T, option_type) - price

    if f_low == 0:
        return low
    if f_high == 0:
        return high
    if f_low * f_high > 0:
        raise ValueError("Volatility bracket does not contain a root; widen [lower, upper].")

    sigma = 0.5 * (low + high)
    for _ in range(max_iter):
        model_price = bs_price(S, K, r, q, sigma, T, option_type)
        diff = model_price - price
        if abs(diff) < tol:
            return float(sigma)

        take_newton = method == "hybrid"
        if take_newton:
            vega = bs_vega(S, K, r, q, sigma, T)
            if vega > 1e-10:
                sigma_newton = sigma - diff / vega
                if low < sigma_newton < high:
                    sigma = sigma_newton
                    continue

        if diff > 0:
            high = sigma
        else:
            low = sigma
        sigma = 0.5 * (low + high)

        if high - low < tol:
            return float(sigma)

    raise RuntimeError("Implied volatility solver did not converge.")


def implied_vol_surface_from_prices(
    prices_df: pd.DataFrame,
    S: float,
    r: float,
    q: float,
    T: float,
    method: Method = "hybrid",
) -> pd.DataFrame:
    """Compute implied vols for a table of option prices.

    Expected input columns are ``strike``, ``option_type``, and ``price``.
    Returns the same table with an ``implied_vol`` column.
    """

    required = {"strike", "option_type", "price"}
    missing = required.difference(prices_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = prices_df.copy()
    out["implied_vol"] = out.apply(
        lambda row: implied_vol(
            price=float(row["price"]),
            S=S,
            K=float(row["strike"]),
            r=r,
            q=q,
            T=T,
            option_type=str(row["option_type"]),
            method=method,
        ),
        axis=1,
    )
    return out
