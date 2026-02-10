"""Finite-difference pricing for the Black-Scholes PDE."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .black_scholes import bs_price


def _boundary_value(
    S_max: float,
    K: float,
    r: float,
    q: float,
    T: float,
    t: float,
    option_type: str,
) -> tuple[float, float]:
    tau = T - t
    if option_type.lower() == "call":
        return 0.0, S_max * math.exp(-q * tau) - K * math.exp(-r * tau)
    if option_type.lower() == "put":
        return K * math.exp(-r * tau), 0.0
    raise ValueError("option_type must be 'call' or 'put'.")


def _thomas_solver(lower: np.ndarray, diag: np.ndarray, upper: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve tridiagonal system Ax=b via Thomas algorithm."""

    n = diag.size
    if n == 1:
        return rhs / diag

    c_prime = np.zeros(n - 1)
    d_prime = np.zeros(n)

    c_prime[0] = upper[0] / diag[0]
    d_prime[0] = rhs[0] / diag[0]

    for i in range(1, n - 1):
        denom = diag[i] - lower[i - 1] * c_prime[i - 1]
        c_prime[i] = upper[i] / denom
        d_prime[i] = (rhs[i] - lower[i - 1] * d_prime[i - 1]) / denom

    denom_last = diag[-1] - lower[-1] * c_prime[-1]
    d_prime[-1] = (rhs[-1] - lower[-1] * d_prime[-2]) / denom_last

    x = np.zeros(n)
    x[-1] = d_prime[-1]
    for i in range(n - 2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i + 1]
    return x


def fd_price_european_bs(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    option_type: str,
    S_max: float,
    M: int,
    N: int,
    scheme: str = "CN",
) -> dict[str, Any]:
    """Price a European option by finite-difference solution of BS PDE.

    Parameters
    ----------
    M, N : int
        Number of stock and time steps, respectively.
    scheme : str
        ``"CN"`` for Crank-Nicolson or ``"implicit"`` for fully implicit.
    """

    if M < 3 or N < 1:
        raise ValueError("M must be >=3 and N must be >=1.")

    dt = T / N
    dS = S_max / M

    S_grid = np.linspace(0.0, S_max, M + 1)
    t_grid = np.linspace(0.0, T, N + 1)

    if option_type.lower() == "call":
        V = np.maximum(S_grid - K, 0.0)
    elif option_type.lower() == "put":
        V = np.maximum(K - S_grid, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    value_grid = np.zeros((N + 1, M + 1))
    value_grid[N, :] = V

    i = np.arange(1, M)
    alpha = 0.5 * sigma * sigma * i * i
    beta = 0.5 * (r - q) * i

    scheme_u = scheme.upper()
    if scheme_u not in {"CN", "IMPLICIT"}:
        raise ValueError("scheme must be either 'CN' or 'implicit'.")

    for n in range(N - 1, -1, -1):
        t_now = t_grid[n]
        t_next = t_grid[n + 1]
        left_now, right_now = _boundary_value(S_max, K, r, q, T, t_now, option_type)
        left_next, right_next = _boundary_value(S_max, K, r, q, T, t_next, option_type)

        if scheme_u == "IMPLICIT":
            lower = -dt * (alpha - beta)
            diag = 1.0 + dt * (2.0 * alpha + r)
            upper = -dt * (alpha + beta)

            rhs = V[1:M].copy()
            rhs[0] -= lower[0] * left_now
            rhs[-1] -= upper[-1] * right_now

        else:  # Crank-Nicolson
            lower_lhs = -0.5 * dt * (alpha - beta)
            diag_lhs = 1.0 + 0.5 * dt * (2.0 * alpha + r)
            upper_lhs = -0.5 * dt * (alpha + beta)

            lower_rhs = 0.5 * dt * (alpha - beta)
            diag_rhs = 1.0 - 0.5 * dt * (2.0 * alpha + r)
            upper_rhs = 0.5 * dt * (alpha + beta)

            rhs = (
                diag_rhs * V[1:M]
                + lower_rhs * np.concatenate(([left_next], V[1 : M - 1]))
                + upper_rhs * np.concatenate((V[2:M], [right_next]))
            )
            rhs[0] -= lower_lhs[0] * left_now
            rhs[-1] -= upper_lhs[-1] * right_now

            lower, diag, upper = lower_lhs, diag_lhs, upper_lhs

        V_new = np.zeros_like(V)
        V_new[0] = left_now
        V_new[M] = right_now
        V_new[1:M] = _thomas_solver(lower[1:], diag, upper[:-1], rhs)

        V = V_new
        value_grid[n, :] = V

    price = float(np.interp(S0, S_grid, value_grid[0, :]))
    return {
        "price": price,
        "S_grid": S_grid,
        "t_grid": t_grid,
        "value_grid": value_grid,
    }


def fd_convergence_vs_bs(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    option_type: str,
    S_max: float,
    grid_pairs: list[tuple[int, int]],
    scheme: str = "CN",
) -> pd.DataFrame:
    """Evaluate FD convergence by varying (M, N) and comparing to BS."""

    bs_val = bs_price(S0, K, r, q, sigma, T, option_type)
    rows = []
    for M, N in grid_pairs:
        out = fd_price_european_bs(
            S0=S0,
            K=K,
            r=r,
            q=q,
            sigma=sigma,
            T=T,
            option_type=option_type,
            S_max=S_max,
            M=M,
            N=N,
            scheme=scheme,
        )
        rows.append(
            {
                "M": M,
                "N": N,
                "fd_price": out["price"],
                "bs_price": bs_val,
                "abs_error": abs(out["price"] - bs_val),
            }
        )
    return pd.DataFrame(rows)
