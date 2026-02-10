"""Monte Carlo pricing under risk-neutral GBM."""

from __future__ import annotations

import math
import time
from typing import Any

import numpy as np

from .processes import simulate_gbm_path_euler


def _payoff(ST: np.ndarray, K: float, option_type: str) -> np.ndarray:
    if option_type.lower() == "call":
        return np.maximum(ST - K, 0.0)
    if option_type.lower() == "put":
        return np.maximum(K - ST, 0.0)
    raise ValueError("option_type must be 'call' or 'put'.")


def _ci_bounds(samples: np.ndarray, alpha: float = 0.95) -> tuple[float, float, float]:
    z = 1.959963984540054  # 95% Gaussian quantile
    mean = float(np.mean(samples))
    std_error = float(np.std(samples, ddof=1) / math.sqrt(samples.size))
    return mean, mean - z * std_error, mean + z * std_error


def mc_price_european_gbm_terminal(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    option_type: str,
    antithetic: bool = True,
    seed: int | None = None,
) -> dict[str, Any]:
    """Price a European option via terminal GBM simulation with confidence intervals."""

    start = time.perf_counter()
    rng = np.random.default_rng(seed)

    if antithetic:
        half = n_paths // 2
        z_half = rng.standard_normal(half)
        z = np.concatenate([z_half, -z_half])
        if z.size < n_paths:
            z = np.concatenate([z, rng.standard_normal(1)])
    else:
        z = rng.standard_normal(n_paths)

    drift = (r - q - 0.5 * sigma * sigma) * T
    diffusion = sigma * math.sqrt(T) * z
    ST = S0 * np.exp(drift + diffusion)

    discounted = math.exp(-r * T) * _payoff(ST, K, option_type)
    price, ci_low, ci_high = _ci_bounds(discounted)
    std_error = float(np.std(discounted, ddof=1) / math.sqrt(discounted.size))

    return {
        "price": float(price),
        "std_error": std_error,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_paths": int(discounted.size),
        "antithetic": antithetic,
        "runtime_seconds": time.perf_counter() - start,
    }


def mc_price_european_gbm_path_euler(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    n_steps: int,
    option_type: str,
    seed: int | None = None,
) -> dict[str, Any]:
    """Price a European option via Euler path simulation and terminal payoff."""

    start = time.perf_counter()
    paths = simulate_gbm_path_euler(
        S0=S0,
        r=r,
        q=q,
        sigma=sigma,
        T=T,
        n_paths=n_paths,
        n_steps=n_steps,
        seed=seed,
    )
    ST = paths[:, -1]
    discounted = math.exp(-r * T) * _payoff(ST, K, option_type)
    price, ci_low, ci_high = _ci_bounds(discounted)
    std_error = float(np.std(discounted, ddof=1) / math.sqrt(discounted.size))

    return {
        "price": float(price),
        "std_error": std_error,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_paths": int(discounted.size),
        "n_steps": n_steps,
        "runtime_seconds": time.perf_counter() - start,
    }


def mc_control_variate_with_terminal_asset(
    S0: float,
    K: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    option_type: str,
    seed: int | None = None,
) -> dict[str, Any]:
    """Optional control variate MC using discounted terminal asset as control.

    The control variate is X = exp(-rT) S_T with known expectation S0 exp(-qT).
    """

    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - q - 0.5 * sigma * sigma) * T + sigma * math.sqrt(T) * z)

    Y = math.exp(-r * T) * _payoff(ST, K, option_type)
    X = math.exp(-r * T) * ST
    EX = S0 * math.exp(-q * T)

    cov = float(np.cov(Y, X, ddof=1)[0, 1])
    var_x = float(np.var(X, ddof=1))
    b = cov / var_x if var_x > 0 else 0.0
    Y_cv = Y - b * (X - EX)

    price, ci_low, ci_high = _ci_bounds(Y_cv)
    std_error = float(np.std(Y_cv, ddof=1) / math.sqrt(Y_cv.size))

    return {
        "price": float(price),
        "std_error": std_error,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_paths": n_paths,
        "control_variate_beta": b,
    }
