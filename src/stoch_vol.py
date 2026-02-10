"""Simple stochastic-volatility simulation and smile extraction."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .implied_vol import implied_vol


def simulate_heston_lite_paths(
    S0: float,
    r: float,
    q: float,
    V0: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    T: float,
    n_paths: int,
    n_steps: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate Heston-lite paths using full truncation for variance."""

    if not (-1.0 <= rho <= 1.0):
        raise ValueError("rho must be in [-1, 1].")

    dt = T / n_steps
    rng = np.random.default_rng(seed)

    z1 = rng.standard_normal((n_paths, n_steps))
    z2 = rng.standard_normal((n_paths, n_steps))

    dW1 = math.sqrt(dt) * z1
    dW2 = math.sqrt(dt) * (rho * z1 + math.sqrt(max(1.0 - rho * rho, 0.0)) * z2)

    S = np.empty((n_paths, n_steps + 1), dtype=float)
    V = np.empty((n_paths, n_steps + 1), dtype=float)
    S[:, 0] = S0
    V[:, 0] = V0

    for t in range(n_steps):
        v_pos = np.maximum(V[:, t], 0.0)
        V[:, t + 1] = V[:, t] + kappa * (theta - v_pos) * dt + xi * np.sqrt(v_pos) * dW2[:, t]
        V[:, t + 1] = np.maximum(V[:, t + 1], 0.0)

        S[:, t + 1] = S[:, t] * np.exp((r - q - 0.5 * v_pos) * dt + np.sqrt(v_pos) * dW1[:, t])

    return S


def sv_option_prices_mc(
    strike_grid: list[float],
    maturities: list[float],
    S0: float,
    r: float,
    q: float,
    V0: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    n_paths: int,
    n_steps_per_year: int = 252,
    option_type: str = "call",
    seed: int | None = 42,
) -> pd.DataFrame:
    """Price options under Heston-lite paths for selected strikes/maturities."""

    rows: list[dict[str, Any]] = []
    for maturity in maturities:
        n_steps = max(2, int(round(maturity * n_steps_per_year)))
        paths = simulate_heston_lite_paths(
            S0=S0,
            r=r,
            q=q,
            V0=V0,
            kappa=kappa,
            theta=theta,
            xi=xi,
            rho=rho,
            T=maturity,
            n_paths=n_paths,
            n_steps=n_steps,
            seed=seed,
        )
        ST = paths[:, -1]
        for K in strike_grid:
            if option_type.lower() == "call":
                payoff = np.maximum(ST - K, 0.0)
            elif option_type.lower() == "put":
                payoff = np.maximum(K - ST, 0.0)
            else:
                raise ValueError("option_type must be 'call' or 'put'.")

            price = math.exp(-r * maturity) * float(np.mean(payoff))
            rows.append(
                {
                    "maturity": maturity,
                    "strike": K,
                    "option_type": option_type.lower(),
                    "price": price,
                }
            )

    return pd.DataFrame(rows)


def implied_vol_smile_from_sv_prices(
    price_table: pd.DataFrame,
    S: float,
    r: float,
    q: float,
    method: str = "hybrid",
) -> pd.DataFrame:
    """Back out implied vols from stochastic-vol model prices."""

    required = {"maturity", "strike", "option_type", "price"}
    missing = required.difference(price_table.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    def _solve(row: pd.Series) -> float:
        try:
            return implied_vol(
                price=float(row["price"]),
                S=S,
                K=float(row["strike"]),
                r=r,
                q=q,
                T=float(row["maturity"]),
                option_type=str(row["option_type"]),
                method=method,
            )
        except Exception:
            return float("nan")

    out = price_table.copy()
    out["implied_vol"] = out.apply(_solve, axis=1)
    return out
