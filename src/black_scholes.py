"""Black-Scholes pricing and Greek analytics for European options."""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm


def _validate_inputs(S: float, K: float, sigma: float, T: float) -> None:
    if S <= 0:
        raise ValueError("Spot price S must be positive.")
    if K <= 0:
        raise ValueError("Strike K must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility sigma must be positive.")
    if T <= 0:
        raise ValueError("Maturity T must be positive.")


def d1_d2(S: float, K: float, r: float, q: float, sigma: float, T: float) -> tuple[float, float]:
    """Compute Black-Scholes d1 and d2 terms.

    Parameters
    ----------
    S, K : float
        Spot and strike.
    r, q : float
        Continuously compounded risk-free and dividend yield rates.
    sigma : float
        Annualized volatility.
    T : float
        Time to maturity in years.
    """

    _validate_inputs(S, K, sigma, T)
    sqrt_t = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return d1, d2


def bs_call_price(S: float, K: float, r: float, q: float, sigma: float, T: float) -> float:
    """Return European call price under Black-Scholes assumptions."""

    d1, d2 = d1_d2(S, K, r, q, sigma, T)
    return float(S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2))


def bs_put_price(S: float, K: float, r: float, q: float, sigma: float, T: float) -> float:
    """Return European put price under Black-Scholes assumptions."""

    d1, d2 = d1_d2(S, K, r, q, sigma, T)
    return float(K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1))


def bs_delta(S: float, K: float, r: float, q: float, sigma: float, T: float, option_type: str) -> float:
    """Return Black-Scholes delta for call or put."""

    d1, _ = d1_d2(S, K, r, q, sigma, T)
    if option_type.lower() == "call":
        return float(math.exp(-q * T) * norm.cdf(d1))
    if option_type.lower() == "put":
        return float(math.exp(-q * T) * (norm.cdf(d1) - 1.0))
    raise ValueError("option_type must be 'call' or 'put'.")


def bs_gamma(S: float, K: float, r: float, q: float, sigma: float, T: float) -> float:
    """Return Black-Scholes gamma."""

    d1, _ = d1_d2(S, K, r, q, sigma, T)
    return float(math.exp(-q * T) * norm.pdf(d1) / (S * sigma * math.sqrt(T)))


def bs_vega(S: float, K: float, r: float, q: float, sigma: float, T: float) -> float:
    """Return Black-Scholes vega per unit volatility."""

    d1, _ = d1_d2(S, K, r, q, sigma, T)
    return float(S * math.exp(-q * T) * norm.pdf(d1) * math.sqrt(T))


def put_call_parity_check(S: float, K: float, r: float, q: float, sigma: float, T: float) -> float:
    """Return parity residual C - P - (S e^{-qT} - K e^{-rT})."""

    call = bs_call_price(S, K, r, q, sigma, T)
    put = bs_put_price(S, K, r, q, sigma, T)
    rhs = S * math.exp(-q * T) - K * math.exp(-r * T)
    return float(call - put - rhs)


def bs_price(S: float, K: float, r: float, q: float, sigma: float, T: float, option_type: str) -> float:
    """Dispatch helper returning call or put price."""

    if option_type.lower() == "call":
        return bs_call_price(S, K, r, q, sigma, T)
    if option_type.lower() == "put":
        return bs_put_price(S, K, r, q, sigma, T)
    raise ValueError("option_type must be 'call' or 'put'.")
