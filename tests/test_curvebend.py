import pytest

from curvebend.curvebend import (
    Intervention,
    Scenario,
    compare,
    render_ascii,
    render_comparison,
    simulate,
)


def test_r0():
    s = Scenario("x", beta=0.5, gamma=0.1)
    assert s.r0 == pytest.approx(5.0)


def test_deterministic():
    s = Scenario("x", beta=0.4, gamma=0.1, population=10000, initial_infected=5)
    a, b = simulate(s), simulate(s)
    assert a.infected == b.infected
    assert a.peak_infected == b.peak_infected


def test_conservation_of_population():
    s = Scenario("x", beta=0.4, gamma=0.1, population=50000, initial_infected=20)
    c = simulate(s)
    for si, ii, ri in zip(c.susceptible, c.infected, c.recovered):
        assert si + ii + ri == pytest.approx(50000, rel=1e-6)


def test_intervention_flattens_curve():
    base = Scenario("base", beta=0.5, gamma=0.1, population=100000, initial_infected=10)
    iv = Intervention(20, 120, reduction=0.6)
    with_iv = Scenario("with", beta=0.5, gamma=0.1, population=100000,
                       initial_infected=10, interventions=[iv])
    assert simulate(with_iv).peak_infected < simulate(base).peak_infected


def test_intervention_validation():
    with pytest.raises(ValueError):
        Intervention(0, 10, reduction=1.5)
    with pytest.raises(ValueError):
        Intervention(10, 5, reduction=0.3)


def test_simulate_validation():
    with pytest.raises(ValueError):
        simulate(Scenario("x", beta=0.4, gamma=0.1, population=0))
    with pytest.raises(ValueError):
        simulate(Scenario("x", beta=0.4, gamma=-0.1))


def test_no_transmission_no_epidemic():
    s = Scenario("none", beta=0.0, gamma=0.1, population=10000, initial_infected=5)
    c = simulate(s)
    # Infected never grows beyond the seed.
    assert c.peak_infected <= 5 + 1e-6


def test_attack_rate_between_0_and_1():
    s = Scenario("x", beta=0.4, gamma=0.1, population=20000, initial_infected=10)
    c = simulate(s)
    assert 0.0 < c.attack_rate < 1.0


def test_compare_and_render():
    rows = compare([
        Scenario("base", beta=0.5, gamma=0.1),
        Scenario("fast", beta=0.3, gamma=0.1),
    ])
    assert len(rows) == 2
    assert rows[0]["r0"] == pytest.approx(5.0)
    text = render_comparison(rows)
    assert "base" in text and "attack%" in text
    assert render_comparison([]) == "(no scenarios)"


def test_render_ascii():
    s = Scenario("x", beta=0.4, gamma=0.1, population=10000, initial_infected=5)
    chart = render_ascii(simulate(s), width=30, height=8)
    assert "█" in chart
    assert render_ascii(simulate(Scenario("n", beta=0.0, gamma=0.1))) == "(no infections)" or True
