"""Tests for Monte Carlo pricing."""

from __future__ import annotations

import numpy as np

from src.black_scholes import bs_call_price
from src.monte_carlo import mc_price_european_gbm_terminal
from src.processes import simulate_gbm_exact


def test_mc_price_within_three_standard_errors_of_bs() -> None:
    bs = bs_call_price(S=100.0, K=100.0, r=0.02, q=0.0, sigma=0.2, T=1.0)
    out = mc_price_european_gbm_terminal(
        S0=100.0,
        K=100.0,
        r=0.02,
        q=0.0,
        sigma=0.2,
        T=1.0,
        n_paths=20_000,
        option_type="call",
        antithetic=True,
        seed=42,
    )
    assert abs(out["price"] - bs) <= 3.0 * out["std_error"]


def test_exact_gbm_terminal_mean_matches_theory() -> None:
    S0, r, q, T = 100.0, 0.03, 0.01, 1.0
    paths = simulate_gbm_exact(S0=S0, r=r, q=q, sigma=0.2, T=T, n_paths=50_000, seed=42)
    empirical = float(np.mean(paths))
    theoretical = S0 * np.exp((r - q) * T)
    assert abs(empirical - theoretical) / theoretical < 0.01
