"""Stochastic process simulation utilities."""

from __future__ import annotations

import math

import numpy as np


def brownian_increments(
    n_paths: int,
    n_steps: int,
    dt: float,
    seed: int | None = None,
) -> np.ndarray:
    """Generate Brownian increments of shape (n_paths, n_steps)."""

    if n_paths <= 0 or n_steps <= 0:
        raise ValueError("n_paths and n_steps must be positive.")
    if dt <= 0:
        raise ValueError("dt must be positive.")

    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_paths, n_steps)) * math.sqrt(dt)


def simulate_gbm_exact(
    S0: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate terminal values S_T from exact GBM distribution."""

    if T <= 0:
        raise ValueError("T must be positive.")

    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths)
    drift = (r - q - 0.5 * sigma * sigma) * T
    diffusion = sigma * math.sqrt(T) * z
    return S0 * np.exp(drift + diffusion)


def simulate_gbm_path_exact(
    S0: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    n_steps: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate full GBM paths with exact per-step lognormal discretization."""

    if n_steps <= 0:
        raise ValueError("n_steps must be positive.")

    dt = T / n_steps
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n_paths, n_steps))
    log_inc = (r - q - 0.5 * sigma * sigma) * dt + sigma * math.sqrt(dt) * z

    paths = np.empty((n_paths, n_steps + 1), dtype=float)
    paths[:, 0] = S0
    paths[:, 1:] = S0 * np.exp(np.cumsum(log_inc, axis=1))
    return paths


def simulate_gbm_path_euler(
    S0: float,
    r: float,
    q: float,
    sigma: float,
    T: float,
    n_paths: int,
    n_steps: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate GBM paths using Euler discretization.

    Note
    ----
    GBM admits an exact discretization; Euler is included for numerical-method demonstrations.
    """

    if n_steps <= 0:
        raise ValueError("n_steps must be positive.")

    dt = T / n_steps
    dW = brownian_increments(n_paths=n_paths, n_steps=n_steps, dt=dt, seed=seed)

    paths = np.empty((n_paths, n_steps + 1), dtype=float)
    paths[:, 0] = S0
    for t in range(n_steps):
        S_t = paths[:, t]
        paths[:, t + 1] = S_t + (r - q) * S_t * dt + sigma * S_t * dW[:, t]
    return paths
