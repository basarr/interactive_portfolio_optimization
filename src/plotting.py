"""Matplotlib plotting helpers for experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _prepare_path(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def plot_binomial_convergence(df: pd.DataFrame, path: str | Path) -> None:
    """Plot CRR convergence to Black-Scholes price."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["N"], df["binomial_price"], marker="o", label="Binomial")
    ax.plot(df["N"], df["bs_price"], linestyle="--", label="Black-Scholes")
    ax.set_xlabel("Tree steps N")
    ax.set_ylabel("Option price")
    ax.set_title("Binomial Convergence")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_implied_vol_recovery(df: pd.DataFrame, path: str | Path) -> None:
    """Plot recovered implied vol versus strike."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["strike"], df["implied_vol"], marker="o", label="Recovered IV")
    if "sigma_true" in df.columns:
        ax.plot(df["strike"], df["sigma_true"], linestyle="--", label="True sigma")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Implied volatility")
    ax.set_title("Implied Volatility Recovery")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_mc_ci(df: pd.DataFrame, bs_price: float, path: str | Path) -> None:
    """Plot Monte Carlo estimates with confidence intervals versus BS benchmark."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(df))
    y = df["price"].to_numpy()
    yerr = np.vstack([y - df["ci_low"].to_numpy(), df["ci_high"].to_numpy() - y])
    ax.errorbar(x, y, yerr=yerr, fmt="o", capsize=3, label="MC 95% CI")
    ax.axhline(bs_price, color="black", linestyle="--", label="Black-Scholes")
    labels = [str(n) for n in df.get("n_paths", pd.Series(x)).to_list()]
    ax.set_xticks(x, labels=labels)
    ax.set_xlabel("Number of paths")
    ax.set_ylabel("Option price")
    ax.set_title("Monte Carlo Confidence Intervals")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_pde_error(df: pd.DataFrame, path: str | Path) -> None:
    """Plot finite-difference absolute error versus grid density."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    grid_size = (df["M"] * df["N"]).to_numpy()
    ax.plot(grid_size, df["abs_error"], marker="o")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Grid size M*N (log)")
    ax.set_ylabel("Absolute error (log)")
    ax.set_title("PDE Error vs Grid Size")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_hedging_error_hist(errors: np.ndarray, path: str | Path) -> None:
    """Plot histogram of hedging error distribution."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(errors, bins=50, alpha=0.8, edgecolor="white")
    ax.set_xlabel("Hedging error")
    ax.set_ylabel("Frequency")
    ax.set_title("Delta-Hedging Error Distribution")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_hedging_tradeoff(df: pd.DataFrame, path: str | Path) -> None:
    """Plot hedging error standard deviation by rebalance interval."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))

    if "tx_cost_per_dollar" in df.columns:
        for tx, sub in df.groupby("tx_cost_per_dollar"):
            sub_sorted = sub.sort_values("rebalance_every_k_steps")
            ax.plot(
                sub_sorted["rebalance_every_k_steps"],
                sub_sorted["std_error"],
                marker="o",
                label=f"tx={tx:.4f}",
            )
    else:
        sub_sorted = df.sort_values("rebalance_every_k_steps")
        ax.plot(sub_sorted["rebalance_every_k_steps"], sub_sorted["std_error"], marker="o")

    ax.set_xlabel("Rebalance every k steps")
    ax.set_ylabel("Std of hedging error")
    ax.set_title("Hedging Tradeoff")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_smile(df: pd.DataFrame, path: str | Path) -> None:
    """Plot implied-vol smile from stochastic-vol prices."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for maturity, sub in df.groupby("maturity"):
        sub = sub.sort_values("strike")
        ax.plot(sub["strike"], sub["implied_vol"], marker="o", label=f"T={maturity}")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Implied volatility")
    ax.set_title("Stochastic-Vol Implied Volatility Smile")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_overlay_distribution(
    unhedged_returns: np.ndarray,
    hedged_returns: np.ndarray,
    path: str | Path,
) -> None:
    """Plot return distributions for unhedged and protected portfolio."""

    save_path = _prepare_path(path)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(unhedged_returns, bins=60, alpha=0.5, label="Unhedged", density=True)
    ax.hist(hedged_returns, bins=60, alpha=0.5, label="Protective Put", density=True)
    ax.set_xlabel("Return")
    ax.set_ylabel("Density")
    ax.set_title("Portfolio Return Distribution")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
