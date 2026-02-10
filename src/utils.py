"""General utilities used across the project."""

from __future__ import annotations

import functools
import os
import time
from typing import Any, Callable, Iterable

import numpy as np


def set_seed(seed: int) -> None:
    """Set NumPy's global random seed for deterministic experiments."""

    np.random.seed(seed)


def ensure_dirs(paths: Iterable[str]) -> None:
    """Create directories if they do not already exist."""

    for path in paths:
        os.makedirs(path, exist_ok=True)


def to_annualized(vol_per_step: float | np.ndarray, dt: float) -> float | np.ndarray:
    """Convert per-step volatility to annualized volatility."""

    if dt <= 0:
        raise ValueError("dt must be positive.")
    return np.asarray(vol_per_step) / np.sqrt(dt)


def to_step_vol(vol_annualized: float | np.ndarray, dt: float) -> float | np.ndarray:
    """Convert annualized volatility to per-step volatility."""

    if dt <= 0:
        raise ValueError("dt must be positive.")
    return np.asarray(vol_annualized) * np.sqrt(dt)


def assert_close(a: float, b: float, tol: float, msg: str = "") -> None:
    """Raise AssertionError when absolute difference exceeds tolerance."""

    if abs(a - b) > tol:
        detail = msg or "Values are not within tolerance."
        raise AssertionError(f"{detail} | a={a}, b={b}, tol={tol}")


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that returns function output and runtime in seconds."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        runtime = time.perf_counter() - start
        if isinstance(result, dict):
            result = dict(result)
            result.setdefault("runtime_seconds", runtime)
            return result
        return result, runtime

    return wrapper
