# curvebend

A deterministic SIR epidemic simulator for building intuition about `R0` and
"flattening the curve". Define scenarios with a transmission rate (`beta`), a
recovery rate (`gamma`), and optional intervention windows that reduce
transmission over a range of days — then compare how they change the peak
infection count, the day it occurs, and the final attack rate.

No randomness: a given scenario always produces the same curve.

## The model

Standard Susceptible / Infected / Recovered compartmental equations, integrated
with a fixed-step Euler method:

```
dS/dt = -beta(t) * S * I / N
dI/dt =  beta(t) * S * I / N - gamma * I
dR/dt =  gamma * I
```

`R0 = beta / gamma`. An `Intervention(start, end, reduction)` multiplies
`beta` by `(1 - reduction)` over `[start, end)` days, so overlapping windows
compound.

## Install

```
pip install -e .
```

## Usage

```
# Baseline vs a 60% lockdown from day 5 to 90, with an ASCII curve
curvebend --beta 0.5 --gamma 0.1 --population 100000 \
          --intervention 5:90:0.6:lockdown --chart
```

With these parameters the baseline peaks around day 27 at ~48k simultaneous
infections; a lockdown starting on day 5 (before the peak) drops the peak to
~16k and pushes it to ~day 97. Starting the *same* lockdown on day 30 — after
the peak has already passed — leaves the peak unchanged and only trims the final
attack rate, which is exactly the timing lesson the tool is meant to make
visible.

Options:
- `--beta`, `--gamma` — transmission and recovery rates (defaults 0.4 / 0.1)
- `--population`, `--initial-infected`, `--days`
- `--intervention START:END:REDUCTION[:LABEL]` — repeatable
- `--chart` — print an ASCII infected curve (UTF-8)

## Python API

```python
from curvebend import Scenario, Intervention, compare, render_comparison

base = Scenario("no-intervention", beta=0.5, gamma=0.1)
lock = Scenario("lockdown", beta=0.5, gamma=0.1,
                interventions=[Intervention(30, 90, 0.6)])
print(render_comparison(compare([base, lock])))
```

## License

MIT
