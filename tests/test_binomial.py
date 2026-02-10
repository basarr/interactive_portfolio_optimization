"""Tests for binomial pricing and replication."""

from __future__ import annotations

from src.binomial import crr_parameters, price_european_binomial, replication_tree
from src.black_scholes import bs_call_price


def test_crr_probability_in_unit_interval() -> None:
    _, _, p = crr_parameters(r=0.02, q=0.0, sigma=0.2, dt=1.0 / 100.0)
    assert 0.0 <= p <= 1.0


def test_binomial_converges_to_bs_for_large_n() -> None:
    bs = bs_call_price(S=100.0, K=100.0, r=0.02, q=0.0, sigma=0.2, T=1.0)
    tree = price_european_binomial(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        N=500,
        option_type="call",
    )
    assert abs(tree - bs) < 1e-2


def test_root_replication_matches_tree_price() -> None:
    out = replication_tree(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        N=5,
        option_type="call",
    )
    assert abs(out["root_replication_gap"]) < 1e-10
