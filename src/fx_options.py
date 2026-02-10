"""FX option pricing via Garman-Kohlhagen."""

from __future__ import annotations

import math

from scipy.stats import norm

from .implied_vol import implied_vol


def _d1_d2(S: float, K: float, rd: float, rf: float, sigma: float, T: float) -> tuple[float, float]:
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive.")
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma and T must be positive.")

    sqrt_t = math.sqrt(T)
    d1 = (math.log(S / K) + (rd - rf + 0.5 * sigma * sigma) * T) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return d1, d2


def gk_call_price(S: float, K: float, rd: float, rf: float, sigma: float, T: float) -> float:
    """Return FX call price under Garman-Kohlhagen."""

    d1, d2 = _d1_d2(S, K, rd, rf, sigma, T)
    return float(S * math.exp(-rf * T) * norm.cdf(d1) - K * math.exp(-rd * T) * norm.cdf(d2))


def gk_put_price(S: float, K: float, rd: float, rf: float, sigma: float, T: float) -> float:
    """Return FX put price under Garman-Kohlhagen."""

    d1, d2 = _d1_d2(S, K, rd, rf, sigma, T)
    return float(K * math.exp(-rd * T) * norm.cdf(-d2) - S * math.exp(-rf * T) * norm.cdf(-d1))


def gk_delta(S: float, K: float, rd: float, rf: float, sigma: float, T: float, option_type: str) -> float:
    """Return spot delta under Garman-Kohlhagen."""

    d1, _ = _d1_d2(S, K, rd, rf, sigma, T)
    if option_type.lower() == "call":
        return float(math.exp(-rf * T) * norm.cdf(d1))
    if option_type.lower() == "put":
        return float(math.exp(-rf * T) * (norm.cdf(d1) - 1.0))
    raise ValueError("option_type must be 'call' or 'put'.")


def gk_implied_vol(price: float, S: float, K: float, rd: float, rf: float, T: float, option_type: str) -> float:
    """Invert GK option price to implied volatility via BS inversion."""

    return implied_vol(price=price, S=S, K=K, r=rd, q=rf, T=T, option_type=option_type)


def gk_put_call_parity_residual(S: float, K: float, rd: float, rf: float, sigma: float, T: float) -> float:
    """Return FX parity residual C - P - (S e^{-rfT} - K e^{-rdT})."""

    call = gk_call_price(S, K, rd, rf, sigma, T)
    put = gk_put_price(S, K, rd, rf, sigma, T)
    rhs = S * math.exp(-rf * T) - K * math.exp(-rd * T)
    return float(call - put - rhs)
