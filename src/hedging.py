"""Delta-hedging simulation under discrete rebalancing."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from .black_scholes import bs_delta, bs_price
from .metrics import cvar
from .processes import simulate_gbm_path_exact


def _payoff(ST: np.ndarray, K: float, option_type: str) -> np.ndarray:
    if option_type.lower() == "call":
        return np.maximum(ST - K, 0.0)
    if option_type.lower() == "put":
        return np.maximum(K - ST, 0.0)
    raise ValueError("option_type must be 'call' or 'put'.")


def _bs_delta_vectorized(
    S: np.ndarray,
    K: float,
    r: float,
    q: float,
    sigma: float,
    tau: float,
    option_type: str,
) -> np.ndarray:
    if tau <= 0:
        if option_type.lower() == "call":
            return np.where(S > K, 1.0, 0.0)
        if option_type.lower() == "put":
            return np.where(S < K, -1.0, 0.0)
        raise ValueError("option_type must be 'call' or 'put'.")

    sqrt_tau = math.sqrt(tau)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma * sigma) * tau) / (sigma * sqrt_tau)
    if option_type.lower() == "call":
        return np.exp(-q * tau) * norm.cdf(d1)
    if option_type.lower() == "put":
        return np.exp(-q * tau) * (norm.cdf(d1) - 1.0)
    raise ValueError("option_type must be 'call' or 'put'.")


def simulate_delta_hedge_on_paths(
    paths: np.ndarray,
    K: float,
    r: float,
    q: float,
    sigma_model: float,
    T: float,
    rebalance_every_k_steps: int,
    option_type: str,
    tx_cost_per_dollar: float = 0.0,
) -> dict[str, Any]:
    """Run a short-option delta hedge on provided spot paths.

    Hedging convention:
    - Short one European option at inception (receive premium).
    - Hold delta shares to hedge option sensitivity.
    - Hedging error = final hedged P&L after settling option payoff.
    """

    if paths.ndim != 2:
        raise ValueError("paths must have shape (n_paths, n_steps + 1).")

    n_paths, n_cols = paths.shape
    n_steps = n_cols - 1
    dt = T / n_steps

    S0 = float(paths[0, 0])
    premium = bs_price(S0, K, r, q, sigma_model, T, option_type)
    delta0 = bs_delta(S0, K, r, q, sigma_model, T, option_type)

    delta_pos = np.full(n_paths, delta0, dtype=float)
    cash = np.full(n_paths, premium - delta0 * S0 - tx_cost_per_dollar * abs(delta0) * S0, dtype=float)

    for step in range(1, n_steps + 1):
        cash *= math.exp(r * dt)
        S_t = paths[:, step]

        is_rebalance = step < n_steps and (step % rebalance_every_k_steps == 0)
        if is_rebalance:
            tau = max(T - step * dt, 1e-12)
            target_delta = _bs_delta_vectorized(S_t, K, r, q, sigma_model, tau, option_type)
            trade = target_delta - delta_pos
            cash -= trade * S_t + tx_cost_per_dollar * np.abs(trade) * S_t
            delta_pos = target_delta

    S_T = paths[:, -1]
    liquidated = cash + delta_pos * S_T - tx_cost_per_dollar * np.abs(delta_pos) * S_T
    payoff = _payoff(S_T, K, option_type)
    errors = liquidated - payoff

    return {
        "errors": errors,
        "mean_error": float(np.mean(errors)),
        "std_error": float(np.std(errors, ddof=1)),
        "q05": float(np.quantile(errors, 0.05)),
        "q95": float(np.quantile(errors, 0.95)),
    }


def simulate_delta_hedge_gbm(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    n_steps: int,
    rebalance_every_k_steps: int,
    option_type: str,
    tx_cost_per_dollar: float,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate delta hedging under exact GBM paths and BS hedge ratios."""

    paths = simulate_gbm_path_exact(
        S0=S0,
        r=r,
        q=q,
        sigma=sigma,
        T=T,
        n_paths=n_paths,
        n_steps=n_steps,
        seed=seed,
    )
    out = simulate_delta_hedge_on_paths(
        paths=paths,
        K=K,
        r=r,
        q=q,
        sigma_model=sigma,
        T=T,
        rebalance_every_k_steps=rebalance_every_k_steps,
        option_type=option_type,
        tx_cost_per_dollar=tx_cost_per_dollar,
    )
    out["paths"] = paths
    return out


def hedging_error_summary(errors: np.ndarray) -> pd.DataFrame:
    """Return summary statistics for hedging-error distribution."""

    return pd.DataFrame(
        [
            {
                "mean": float(np.mean(errors)),
                "std": float(np.std(errors, ddof=1)),
                "median": float(np.median(errors)),
                "q01": float(np.quantile(errors, 0.01)),
                "q05": float(np.quantile(errors, 0.05)),
                "q95": float(np.quantile(errors, 0.95)),
                "q99": float(np.quantile(errors, 0.99)),
                "cvar_95": float(cvar(errors, alpha=0.05)),
            }
        ]
    )


def hedging_experiment_grid(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    n_steps: int,
    rebalance_list: list[int],
    tx_cost_list: list[float],
    option_type: str,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Run a grid of hedging simulations over rebalance and cost settings."""

    base_paths = simulate_gbm_path_exact(
        S0=S0,
        r=r,
        q=q,
        sigma=sigma,
        T=T,
        n_paths=n_paths,
        n_steps=n_steps,
        seed=seed,
    )

    rows = []
    for k in rebalance_list:
        for tx in tx_cost_list:
            out = simulate_delta_hedge_on_paths(
                paths=base_paths,
                K=K,
                r=r,
                q=q,
                sigma_model=sigma,
                T=T,
                rebalance_every_k_steps=k,
                option_type=option_type,
                tx_cost_per_dollar=tx,
            )
            rows.append(
                {
                    "rebalance_every_k_steps": k,
                    "tx_cost_per_dollar": tx,
                    "mean_error": out["mean_error"],
                    "std_error": out["std_error"],
                    "q05": out["q05"],
                    "q95": out["q95"],
                }
            )
    return pd.DataFrame(rows)
