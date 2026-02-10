"""Tests for FX option pricing."""

from __future__ import annotations

from src.fx_options import gk_put_call_parity_residual


def test_gk_put_call_parity() -> None:
    residual = gk_put_call_parity_residual(S=1.10, K=1.10, rd=0.03, rf=0.01, sigma=0.12, T=1.0)
    assert abs(residual) < 1e-10
