"""Deterministic SIR epidemic simulator with intervention scenarios."""
from .curvebend import (
    Curve,
    Intervention,
    Scenario,
    compare,
    render_ascii,
    render_comparison,
    simulate,
)

__all__ = [
    "Curve",
    "Intervention",
    "Scenario",
    "compare",
    "render_ascii",
    "render_comparison",
    "simulate",
]
