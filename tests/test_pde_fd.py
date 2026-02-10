"""Tests for finite-difference PDE pricer."""

from __future__ import annotations

from src.black_scholes import bs_call_price
from src.pde_fd import fd_price_european_bs


def test_fd_price_close_to_bs() -> None:
    bs = bs_call_price(S=100.0, K=100.0, r=0.02, q=0.0, sigma=0.2, T=1.0)
    out = fd_price_european_bs(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        option_type="call",
        S_max=300.0,
        M=200,
        N=200,
        scheme="CN",
    )
    assert abs(out["price"] - bs) < 2e-2
