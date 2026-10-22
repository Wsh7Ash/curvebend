"""Deterministic SIR epidemic simulation with intervention scenarios.

Models a closed population through the classic Susceptible/Infected/Recovered
compartmental equations using fixed-step Euler integration. Scenarios can
introduce interventions (a reduction in the transmission rate) over specific
day ranges, letting you compare how "flattening the curve" changes the peak
infection count, the day it occurs, and the final attack rate.

Fully deterministic — no randomness — so a given scenario always yields the same
curve. Useful for building intuition about R0 and intervention timing.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Intervention:
    """Reduce transmission by ``reduction`` (0..1) between ``start`` and ``end`` day."""
    start: float
    end: float
    reduction: float
    label: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.reduction <= 1.0:
            raise ValueError("reduction must be within [0, 1]")
        if self.end < self.start:
            raise ValueError("end must be >= start")

    def applies_on(self, day: float) -> bool:
        return self.start <= day < self.end


@dataclass
class Scenario:
    name: str
    beta: float           # transmission rate (per day)
    gamma: float          # recovery rate (per day)
    population: int = 100_000
    initial_infected: int = 10
    days: int = 180
    dt: float = 0.1       # integration step (days)
    interventions: list[Intervention] = field(default_factory=list)

    @property
    def r0(self) -> float:
        return self.beta / self.gamma

    def beta_at(self, day: float) -> float:
        factor = 1.0
        for iv in self.interventions:
            if iv.applies_on(day):
                factor *= 1.0 - iv.reduction
        return self.beta * factor


@dataclass
class Curve:
    times: list[float]
    susceptible: list[float]
    infected: list[float]
    recovered: list[float]
    population: int = 0

    @property
    def peak_infected(self) -> float:
        return max(self.infected)

    @property
    def peak_day(self) -> float:
        return self.times[self.infected.index(max(self.infected))]

    @property
    def attack_rate(self) -> float:
        """Fraction of the population ever infected (1 - final susceptible/total)."""
        if self.population <= 0:
            return 0.0
        return 1.0 - (self.susceptible[-1] / self.population)


def simulate(scenario: Scenario) -> Curve:
    """Run a scenario with fixed-step Euler integration of the SIR equations."""
    if scenario.population <= 0:
        raise ValueError("population must be positive")
    if scenario.initial_infected < 0 or scenario.initial_infected > scenario.population:
        raise ValueError("initial_infected must be within [0, population]")
    if scenario.gamma <= 0 or scenario.beta < 0:
        raise ValueError("gamma must be > 0 and beta >= 0")
    if scenario.dt <= 0:
        raise ValueError("dt must be positive")

    n = scenario.population
    s = float(n - scenario.initial_infected)
    i = float(scenario.initial_infected)
    r = 0.0

    times = [0.0]
    susceptible = [s]
    infected = [i]
    recovered = [r]

    steps = int(round(scenario.days / scenario.dt))
    for step in range(1, steps + 1):
        day = step * scenario.dt
        beta = scenario.beta_at(day)
        # Standard SIR derivatives.
        ds = -beta * s * i / n
        dr = scenario.gamma * i
        di = -ds - dr
        s += ds * scenario.dt
        i += di * scenario.dt
        r += dr * scenario.dt
        # Guard against tiny negative drift from Euler error.
        s = max(s, 0.0)
        i = max(i, 0.0)
        r = max(r, 0.0)
        times.append(day)
        susceptible.append(s)
        infected.append(i)
        recovered.append(r)

    return Curve(times, susceptible, infected, recovered, population=n)


def compare(scenarios: list[Scenario]) -> list[dict]:
    """Simulate several scenarios and return their headline metrics."""
    rows = []
    for sc in scenarios:
        curve = simulate(sc)
        rows.append({
            "name": sc.name,
            "r0": round(sc.r0, 3),
            "peak_infected": round(curve.peak_infected),
            "peak_day": round(curve.peak_day, 1),
            "attack_rate_pct": round(curve.attack_rate * 100, 1),
        })
    return rows


def render_comparison(rows: list[dict]) -> str:
    if not rows:
        return "(no scenarios)"
    header = f"{'scenario':<22} {'R0':>6} {'peak':>8} {'day':>6} {'attack%':>8}"
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(
            f"{row['name']:<22} {row['r0']:>6} {row['peak_infected']:>8} "
            f"{row['peak_day']:>6} {row['attack_rate_pct']:>8}"
        )
    return "\n".join(lines)


def render_ascii(curve: Curve, width: int = 60, height: int = 12) -> str:
    """Render the infected curve as a coarse ASCII chart."""
    peak = curve.peak_infected
    if peak <= 0:
        return "(no infections)"
    cols = min(width, len(curve.infected))
    # Downsample to `cols` buckets, taking the max in each.
    step = len(curve.infected) / cols
    buckets = []
    for c in range(cols):
        lo = int(c * step)
        hi = max(lo + 1, int((c + 1) * step))
        buckets.append(max(curve.infected[lo:hi]))

    rows_out = []
    for row in range(height, 0, -1):
        threshold = peak * row / height
        line = "".join("█" if v >= threshold else " " for v in buckets)
        rows_out.append(line)
    return "\n".join(rows_out)
