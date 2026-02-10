"""Cox-Ross-Rubinstein binomial pricing and replication."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .black_scholes import bs_price


def crr_parameters(r: float, q: float, sigma: float, dt: float) -> tuple[float, float, float]:
    """Return CRR up/down multipliers and risk-neutral probability."""

    if sigma <= 0:
        raise ValueError("sigma must be positive.")
    if dt <= 0:
        raise ValueError("dt must be positive.")

    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp((r - q) * dt) - d) / (u - d)

    if not (0.0 <= p <= 1.0):
        raise ValueError(
            "Risk-neutral probability out of bounds. Increase N or verify inputs so no-arbitrage holds."
        )
    return u, d, p


def _payoff(stock: np.ndarray, K: float, option_type: str) -> np.ndarray:
    if option_type.lower() == "call":
        return np.maximum(stock - K, 0.0)
    if option_type.lower() == "put":
        return np.maximum(K - stock, 0.0)
    raise ValueError("option_type must be 'call' or 'put'.")


def price_european_binomial(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    N: int,
    option_type: str,
) -> float:
    """Price a European option with a CRR tree under risk-neutral valuation."""

    if N <= 0:
        raise ValueError("N must be positive.")

    dt = T / N
    u, d, p = crr_parameters(r=r, q=q, sigma=sigma, dt=dt)
    disc = math.exp(-r * dt)

    j = np.arange(N + 1)
    stock_terminal = S0 * (u ** j) * (d ** (N - j))
    values = _payoff(stock_terminal, K, option_type)

    for _ in range(N, 0, -1):
        values = disc * (p * values[1:] + (1.0 - p) * values[:-1])
    return float(values[0])


def replication_one_step(Su: float, Sd: float, Vu: float, Vd: float, r: float, dt: float) -> tuple[float, float]:
    """Solve one-step replication weights (delta, bond)."""

    if Su == Sd:
        raise ValueError("Su and Sd must differ for replication.")

    delta = (Vu - Vd) / (Su - Sd)
    bond = math.exp(-r * dt) * (Vu - delta * Su)
    return float(delta), float(bond)


def replication_tree(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    N: int,
    option_type: str,
) -> dict[str, Any]:
    """Construct CRR tree and node-wise replication holdings.

    Returns a dictionary with tree layers for stock values, option values,
    deltas, bonds, and root consistency diagnostics.
    """

    dt = T / N
    u, d, p = crr_parameters(r=r, q=q, sigma=sigma, dt=dt)
    disc = math.exp(-r * dt)

    stock_layers: list[np.ndarray] = []
    for step in range(N + 1):
        j = np.arange(step + 1)
        stock_layers.append(S0 * (u ** j) * (d ** (step - j)))

    option_layers: list[np.ndarray] = [np.array([]) for _ in range(N + 1)]
    delta_layers: list[np.ndarray] = [np.array([]) for _ in range(N)]
    bond_layers: list[np.ndarray] = [np.array([]) for _ in range(N)]

    option_layers[N] = _payoff(stock_layers[N], K, option_type)

    for step in range(N - 1, -1, -1):
        next_values = option_layers[step + 1]
        option_layers[step] = disc * (p * next_values[1:] + (1.0 - p) * next_values[:-1])

        Su = stock_layers[step + 1][1:]
        Sd = stock_layers[step + 1][:-1]
        Vu = next_values[1:]
        Vd = next_values[:-1]

        delta = (Vu - Vd) / (Su - Sd)
        bond = np.exp(-r * dt) * (Vu - delta * Su)
        delta_layers[step] = delta
        bond_layers[step] = bond

    root_price = float(option_layers[0][0])
    root_repl = float(delta_layers[0][0] * S0 + bond_layers[0][0])

    return {
        "price": root_price,
        "deltas": delta_layers,
        "bonds": bond_layers,
        "option_values": option_layers,
        "stock_values": stock_layers,
        "root_replication_price": root_repl,
        "root_replication_gap": root_repl - root_price,
    }


def convergence_table_to_bs(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    option_type: str,
    N_values: list[int],
) -> pd.DataFrame:
    """Create convergence table comparing CRR prices to Black-Scholes."""

    bs_val = bs_price(S0, K, r, q, sigma, T, option_type)
    rows = []
    for n in N_values:
        tree_val = price_european_binomial(S0, K, r, q, sigma, T, n, option_type)
        rows.append(
            {
                "N": n,
                "binomial_price": tree_val,
                "bs_price": bs_val,
                "abs_error": abs(tree_val - bs_val),
                "signed_error": tree_val - bs_val,
            }
        )
    return pd.DataFrame(rows)
