"""Tests for market-data integrity helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from src.market_data import assert_price_data_ready, price_data_quality_report, price_gap_report


def _sample_prices() -> pd.DataFrame:
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])
    return pd.DataFrame({"ASML": [100.0, 101.0, 100.5, 102.0]}, index=idx)


def test_price_gap_report_detects_large_gap() -> None:
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-20"])
    prices = pd.DataFrame({"ASML": [100.0, 101.0, 102.0]}, index=idx)
    gaps = price_gap_report(prices, max_gap_days=5)
    assert len(gaps) == 1
    assert int(gaps.loc[0, "gap_days"]) == 17


def test_price_data_quality_report_has_expected_fields() -> None:
    report = price_data_quality_report(_sample_prices(), ticker="ASML")
    expected_cols = {
        "ticker",
        "n_obs",
        "first_date",
        "last_date",
        "has_missing_values",
        "is_index_monotonic",
        "has_duplicate_index",
        "max_calendar_gap_days",
    }
    assert expected_cols.issubset(report.columns)
    assert int(report.loc[0, "n_obs"]) == 4


def test_assert_price_data_ready_passes_valid_data() -> None:
    assert_price_data_ready(_sample_prices(), ticker="ASML", start="2020-01-01", min_obs=3, max_gap_days=5)


def test_assert_price_data_ready_fails_for_duplicate_index() -> None:
    prices = _sample_prices()
    bad = pd.concat([prices, prices.iloc[[0]]], axis=0).sort_index()
    with pytest.raises(ValueError, match="duplicates"):
        assert_price_data_ready(bad, ticker="ASML", start="2020-01-01", min_obs=3, max_gap_days=5)


def test_assert_price_data_ready_fails_for_late_start() -> None:
    idx = pd.to_datetime(["2020-03-01", "2020-03-02", "2020-03-03", "2020-03-04"])
    prices = pd.DataFrame({"ASML": [100.0, 101.0, 102.0, 103.0]}, index=idx)
    with pytest.raises(ValueError, match="starts too late"):
        assert_price_data_ready(prices, ticker="ASML", start="2020-01-01", min_obs=3, max_gap_days=5)
