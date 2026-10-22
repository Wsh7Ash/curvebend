"""Command-line interface for curvebend."""
from __future__ import annotations

import argparse
import sys

from .curvebend import Intervention, Scenario, compare, render_ascii, render_comparison, simulate


def _ensure_utf8_stdout() -> None:
    # The ASCII chart uses Unicode block characters; reconfigure so this works
    # on Windows consoles that default to a legacy code page.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="curvebend",
        description="Compare SIR epidemic scenarios and their interventions.",
    )
    parser.add_argument("--beta", type=float, default=0.4, help="Transmission rate (default 0.4)")
    parser.add_argument("--gamma", type=float, default=0.1, help="Recovery rate (default 0.1)")
    parser.add_argument("--population", type=int, default=100_000, help="Population (default 100000)")
    parser.add_argument("--initial-infected", type=int, default=10, help="Initial infected (default 10)")
    parser.add_argument("--days", type=int, default=180, help="Days to simulate (default 180)")
    parser.add_argument(
        "--intervention", action="append", default=[],
        metavar="START:END:REDUCTION[:LABEL]",
        help="Add an intervention window, e.g. 30:90:0.5:lockdown (repeatable)",
    )
    parser.add_argument("--chart", action="store_true", help="Print an ASCII infected curve")
    args = parser.parse_args(argv)

    interventions = []
    for spec in args.intervention:
        parts = spec.split(":")
        if len(parts) not in (3, 4):
            parser.error(f"bad intervention spec {spec!r}")
        start, end, reduction = float(parts[0]), float(parts[1]), float(parts[2])
        label = parts[3] if len(parts) == 4 else ""
        interventions.append(Intervention(start, end, reduction, label))

    base = Scenario(
        "no-intervention", args.beta, args.gamma,
        population=args.population, initial_infected=args.initial_infected,
        days=args.days,
    )
    scenarios = [base]
    if interventions:
        scenarios.append(Scenario(
            "with-intervention", args.beta, args.gamma,
            population=args.population, initial_infected=args.initial_infected,
            days=args.days, interventions=interventions,
        ))

    _ensure_utf8_stdout()
    rows = compare(scenarios)
    print(render_comparison(rows))
    if args.chart:
        print()
        print(f"infected curve — {scenarios[-1].name}")
        print(render_ascii(simulate(scenarios[-1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
