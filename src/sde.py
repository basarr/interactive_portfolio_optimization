"""Numerical SDE scheme helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .processes import simulate_gbm_path_euler, simulate_gbm_path_exact


def euler_scheme_gbm_step(S: float, r: float, q: float, sigma: float, dt: float, dW: float) -> float:
    """Apply one Euler step for GBM SDE."""

    return S + (r - q) * S * dt + sigma * S * dW


def error_vs_step_count_experiment(
    S0: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    step_counts: list[int],
    seed: int | None = 42,
) -> pd.DataFrame:
    """Compare Euler and exact GBM terminal moment errors over step counts."""

    rows: list[dict[str, float]] = []
    theoretical_mean = S0 * float(np.exp((r - q) * T))

    for n_steps in step_counts:
        euler_paths = simulate_gbm_path_euler(S0, r, q, sigma, T, n_paths, n_steps, seed=seed)
        exact_paths = simulate_gbm_path_exact(S0, r, q, sigma, T, n_paths, n_steps, seed=seed)

        euler_mean = float(euler_paths[:, -1].mean())
        exact_mean = float(exact_paths[:, -1].mean())

        rows.append(
            {
                "n_steps": int(n_steps),
                "euler_mean_ST": euler_mean,
                "exact_mean_ST": exact_mean,
                "theoretical_mean_ST": theoretical_mean,
                "abs_error_euler_mean": abs(euler_mean - theoretical_mean),
                "abs_error_exact_mean": abs(exact_mean - theoretical_mean),
            }
        )

    return pd.DataFrame(rows)
