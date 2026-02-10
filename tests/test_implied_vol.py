"""Tests for implied volatility inversion."""

from __future__ import annotations

from src.black_scholes import bs_call_price
from src.implied_vol import implied_vol


def test_recover_sigma_from_synthetic_prices() -> None:
    sigma_true = 0.24
    strikes = [80.0, 100.0, 120.0]
    for strike in strikes:
        price = bs_call_price(S=100.0, K=strike, r=0.02, q=0.0, sigma=sigma_true, T=1.0)
        sigma_hat = implied_vol(
            price=price,
            S=100.0,
            K=strike,
            r=0.02,
            q=0.0,
            T=1.0,
            option_type="call",
        )
        assert abs(sigma_hat - sigma_true) < 1e-6
