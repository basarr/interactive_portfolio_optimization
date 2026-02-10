"""Portfolio overlay experiments with a protective put."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .black_scholes import bs_put_price
from .metrics import summary_table
from .processes import simulate_gbm_path_exact


def protective_put_overlay_simulation(
    S0: float,
    r: float,
    q: float,
    sigma: float,
    T_sim: float,
    K_put: float,
    T_put: float,
    notional: float,
    premium_budget_fraction: float,
    n_paths: int,
    n_steps: int,
    seed: int | None = 42,
) -> dict[str, Any]:
    """Simulate unhedged and protective-put overlay portfolio outcomes.

    The hedge amount is selected such that initial premium spent does not exceed
    ``premium_budget_fraction * notional`` and does not exceed full notional coverage.
    """

    if T_put > T_sim:
        raise ValueError("T_put must be <= T_sim in this implementation.")

    paths = simulate_gbm_path_exact(
        S0=S0,
        r=r,
        q=q,
        sigma=sigma,
        T=T_sim,
        n_paths=n_paths,
        n_steps=n_steps,
        seed=seed,
    )

    units_underlying = notional / S0
    put_premium = bs_put_price(S0, K_put, r, q, sigma, T_put)
    budget = premium_budget_fraction * notional
    hedge_units = min(units_underlying, budget / put_premium if put_premium > 0 else 0.0)

    idx_put = int(round((T_put / T_sim) * n_steps))
    idx_put = max(1, min(idx_put, n_steps))

    S_put = paths[:, idx_put]
    S_T = paths[:, -1]

    unhedged_terminal = units_underlying * S_T
    put_payoff = hedge_units * np.maximum(K_put - S_put, 0.0)

    # Put payoff is received at T_put; grow to T_sim for consistent horizon comparison.
    put_payoff_grown = put_payoff * math.exp(r * (T_sim - T_put))

    premium_paid = hedge_units * put_premium
    hedged_terminal = unhedged_terminal - premium_paid + put_payoff_grown

    unhedged_returns = unhedged_terminal / notional - 1.0
    hedged_returns = hedged_terminal / notional - 1.0

    return {
        "unhedged_returns": unhedged_returns,
        "hedged_returns": hedged_returns,
        "hedge_units": hedge_units,
        "premium_paid": premium_paid,
        "premium_budget": budget,
        "coverage_ratio": hedge_units / units_underlying if units_underlying > 0 else 0.0,
    }


def overlay_risk_metrics(unhedged_returns: np.ndarray, hedged_returns: np.ndarray) -> pd.DataFrame:
    """Return side-by-side summary metrics for unhedged vs overlay returns."""

    unhedged = summary_table(unhedged_returns)
    hedged = summary_table(hedged_returns)
    unhedged.index = ["unhedged"]
    hedged.index = ["protective_put"]
    return pd.concat([unhedged, hedged], axis=0)
