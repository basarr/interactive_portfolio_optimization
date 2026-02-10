"""Tests for Black-Scholes analytics."""

from __future__ import annotations

from src.black_scholes import bs_call_price, bs_delta, bs_put_price, put_call_parity_check


def test_put_call_parity_close() -> None:
    residual = put_call_parity_check(S=100, K=100, r=0.02, q=0.01, sigma=0.2, T=1.0)
    assert abs(residual) < 1e-10


def test_call_price_positive() -> None:
    price = bs_call_price(S=100, K=95, r=0.02, q=0.00, sigma=0.2, T=1.0)
    assert price > 0


def test_delta_sign_sanity() -> None:
    call_delta = bs_delta(S=100, K=100, r=0.02, q=0.00, sigma=0.2, T=1.0, option_type="call")
    put_delta = bs_delta(S=100, K=100, r=0.02, q=0.00, sigma=0.2, T=1.0, option_type="put")
    assert 0 < call_delta < 1
    assert -1 < put_delta < 0
    assert bs_put_price(S=100, K=100, r=0.02, q=0.00, sigma=0.2, T=1.0) > 0
