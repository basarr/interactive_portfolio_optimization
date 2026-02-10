"""Tests for delta-hedging behavior."""

from __future__ import annotations

from src.hedging import simulate_delta_hedge_gbm


def test_more_frequent_rebalancing_reduces_error_std_without_costs() -> None:
    daily = simulate_delta_hedge_gbm(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        n_paths=6_000,
        n_steps=252,
        rebalance_every_k_steps=1,
        option_type="call",
        tx_cost_per_dollar=0.0,
        seed=42,
    )
    monthly = simulate_delta_hedge_gbm(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        n_paths=6_000,
        n_steps=252,
        rebalance_every_k_steps=21,
        option_type="call",
        tx_cost_per_dollar=0.0,
        seed=42,
    )
    assert daily["std_error"] < monthly["std_error"]


def test_transaction_costs_reduce_short_hedged_book_pnl() -> None:
    without_cost = simulate_delta_hedge_gbm(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        n_paths=4_000,
        n_steps=252,
        rebalance_every_k_steps=5,
        option_type="call",
        tx_cost_per_dollar=0.0,
        seed=123,
    )
    with_cost = simulate_delta_hedge_gbm(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        n_paths=4_000,
        n_steps=252,
        rebalance_every_k_steps=5,
        option_type="call",
        tx_cost_per_dollar=0.002,
        seed=123,
    )
    assert with_cost["mean_error"] < without_cost["mean_error"]
