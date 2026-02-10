"""Tests for risk metrics."""

from __future__ import annotations

import numpy as np

from src.metrics import cvar, max_drawdown


def test_max_drawdown_toy_series() -> None:
    returns = np.array([0.10, -0.20, 0.05, -0.10])
    # Wealth path: 1.10, 0.88, 0.924, 0.8316 -> peak=1.10, trough=0.8316, drawdown=-24.4%
    dd = max_drawdown(returns)
    assert abs(dd - (-0.244)) < 1e-3


def test_cvar_toy_distribution() -> None:
    values = np.array([-4.0, -3.0, -2.0, 1.0, 2.0, 3.0])
    tail = cvar(values, alpha=0.2)
    assert tail <= -3.0
