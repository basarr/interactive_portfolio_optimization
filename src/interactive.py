"""Minimal ipywidgets helpers for notebook interactivity."""

from __future__ import annotations

from typing import Callable

import ipywidgets as widgets
from IPython.display import display

from .black_scholes import bs_price
from .monte_carlo import mc_price_european_gbm_terminal


def pricing_widget(on_update: Callable[..., None] | None = None) -> widgets.VBox:
    """Create a lightweight pricing widget for BS and fast MC estimates."""

    S = widgets.FloatSlider(description="S", value=100.0, min=50.0, max=150.0, step=1.0)
    K = widgets.FloatSlider(description="K", value=100.0, min=50.0, max=150.0, step=1.0)
    sigma = widgets.FloatSlider(description="sigma", value=0.2, min=0.05, max=1.0, step=0.01)
    T = widgets.FloatSlider(description="T", value=1.0, min=0.05, max=2.0, step=0.05)
    option_type = widgets.Dropdown(description="type", options=["call", "put"], value="call")
    fast_paths = widgets.IntSlider(description="MC paths", value=20_000, min=2_000, max=60_000, step=2_000)
    out = widgets.Output()

    def _render(*_: object) -> None:
        with out:
            out.clear_output(wait=True)
            bs = bs_price(S.value, K.value, 0.02, 0.0, sigma.value, T.value, option_type.value)
            mc = mc_price_european_gbm_terminal(
                S0=S.value,
                K=K.value,
                r=0.02,
                q=0.0,
                sigma=sigma.value,
                T=T.value,
                n_paths=fast_paths.value,
                option_type=option_type.value,
                antithetic=True,
                seed=42,
            )
            print(f"BS price: {bs:.4f}")
            print(f"MC price: {mc['price']:.4f} | 95% CI [{mc['ci_low']:.4f}, {mc['ci_high']:.4f}]")
        if on_update is not None:
            on_update(S.value, K.value, sigma.value, T.value, option_type.value)

    for w in [S, K, sigma, T, option_type, fast_paths]:
        w.observe(_render, names="value")

    _render()
    box = widgets.VBox([widgets.HBox([S, K, sigma]), widgets.HBox([T, option_type, fast_paths]), out])
    return box


def display_pricing_widget() -> None:
    """Display the pricing widget in notebooks."""

    display(pricing_widget())
