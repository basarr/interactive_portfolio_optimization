"""Project configuration defaults for derivatives-risk-lab."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LabConfig:
    """Container for default parameters used across modules and notebooks."""

    SEED: int = 42
    RESULTS_DIR: str = "results"
    FIG_DIR: str = "results/figures"
    TABLE_DIR: str = "results/tables"

    R: float = 0.02
    Q: float = 0.00
    DAY_COUNT: int = 252
    DT: float = 1.0 / 252.0

    S0: float = 100.0
    SIGMA: float = 0.20
    T: float = 1.0
    K: float = 100.0

    N_STEPS_TREE: int = 200

    N_PATHS: int = 200_000
    N_STEPS_MC: int = 252
    USE_ANTITHETIC: bool = True
    USE_CONTROL_VARIATE: bool = False

    S_MAX_MULT: float = 3.0
    N_S_GRID: int = 400
    N_T_GRID: int = 400
    FD_SCHEME: str = "CN"

    IV_LOWER: float = 1e-6
    IV_UPPER: float = 5.0
    IV_TOL: float = 1e-8
    IV_MAX_ITER: int = 100

    HEDGE_REBALANCE_STEPS: list[int] = field(default_factory=lambda: [1, 2, 5, 10, 21])
    TX_COST_PER_DOLLAR: float = 0.0
    OPTION_TYPE: str = "call"

    SV_MODEL: str = "heston_lite"
    V0: float = 0.04
    KAPPA: float = 2.0
    THETA: float = 0.04
    XI: float = 0.5
    RHO: float = -0.6
    SV_EULER_STEPS: int = 252
    SV_PATHS: int = 100_000

    S0_FX: float = 1.10
    RD: float = 0.03
    RF: float = 0.01
    SIGMA_FX: float = 0.12
    T_FX: float = 1.0
    K_FX: float = 1.10

    PORTFOLIO_NOTIONAL: float = 1_000_000.0
    HEDGE_RATIO: float = 1.0
    PROTECTIVE_PUT_STRIKE: float = 95.0
    PUT_MATURITY: float = 0.25
    HEDGE_BUDGET_FRACTION: float = 0.02


CONFIG = LabConfig()


def config_dict(*, fast_mode: bool = False) -> dict[str, Any]:
    """Return configuration as a mutable dictionary.

    Parameters
    ----------
    fast_mode:
        If True, reduce simulation sizes for interactive responsiveness.
    """

    cfg = asdict(CONFIG)
    if fast_mode:
        cfg["N_PATHS"] = 20_000
        cfg["SV_PATHS"] = 20_000
        cfg["N_S_GRID"] = 200
        cfg["N_T_GRID"] = 200
    return cfg
