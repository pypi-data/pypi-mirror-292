from numpy import array, inf
from numpy.testing import assert_almost_equal
from pytest import mark

from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.utils.descriptive_stats import (
    _calc_confidence_level, calc_confidence_level_monte_carlo, calc_descriptive_stats, calc_precision_monte_carlo,
    calc_required_iterations_monte_carlo, calc_z_critical
)

# confidence_level, n_sided, z_critical
CONFIDENCE_INTERVAL_PARAMS = [
    # 1 sided
    (0, 1, -inf),
    (50, 1, 0),
    (80, 1, 0.8416),
    (90, 1, 1.2816),
    (95, 1, 1.6449),
    (99, 1, 2.3263),
    (100, 1, inf),
    # 2 sided
    (0, 2, 0),
    (50, 2, 0.6745),
    (80, 2, 1.2816),
    (90, 2, 1.6449),
    (95, 2, 1.9600),
    (99, 2, 2.5758),
    (100, 2, inf)
]


@mark.parametrize(
    "confidence_level, n_sided, z_critical",
    CONFIDENCE_INTERVAL_PARAMS,
    ids=[f"z={z}, n={n}" for _, n, z in CONFIDENCE_INTERVAL_PARAMS]
)
def test_calc_confidence_level(confidence_level, n_sided, z_critical):
    result = _calc_confidence_level(z_critical, n_sided=n_sided)
    assert_almost_equal(result, confidence_level, decimal=2)


@mark.parametrize(
    "confidence_level, n_sided, z_critical",
    CONFIDENCE_INTERVAL_PARAMS,
    ids=[f"conf={conf}, n={n}" for conf, n, _ in CONFIDENCE_INTERVAL_PARAMS]
)
def test_calc_z_critical(confidence_level, n_sided, z_critical):
    result = calc_z_critical(confidence_level, n_sided=n_sided)
    assert_almost_equal(result, z_critical, decimal=4)


# confidence_level, n_iterations, precision, sd
MONTE_CARLO_PARAMS = [
    (95, 80767, 0.01, 1.45),
    (95, 1110, 0.01, 0.17),
    (99, 1917, 0.01, 0.17),
    (50, 102, 100.18, 1500)
]


@mark.parametrize(
    "confidence_level, n_iterations, precision, sd",
    MONTE_CARLO_PARAMS,
    ids=[f"n={n}, prec={prec}, sd={sd}" for _, n, prec, sd in MONTE_CARLO_PARAMS]
)
def test_calc_confidence_level_monte_carlo(confidence_level, n_iterations, precision, sd):
    result = calc_confidence_level_monte_carlo(n_iterations, precision, sd,)
    assert_almost_equal(result, confidence_level, decimal=2)


@mark.parametrize(
    "confidence_level, n_iterations, precision, sd",
    MONTE_CARLO_PARAMS,
    ids=[f"conf={conf}, prec={prec}, sd={sd}" for conf, _, prec, sd in MONTE_CARLO_PARAMS]
)
def test_calc_required_iterations_monte_carlo(confidence_level, n_iterations, precision, sd):
    result = calc_required_iterations_monte_carlo(confidence_level, precision, sd)
    assert result == n_iterations


@mark.parametrize(
    "confidence_level, n_iterations, precision, sd",
    MONTE_CARLO_PARAMS,
    ids=[f"conf={conf}, n={n}, sd={sd}" for conf, n, _, sd in MONTE_CARLO_PARAMS]
)
def test_calc_precision_monte_carlo(confidence_level, n_iterations, precision, sd):
    result = calc_precision_monte_carlo(confidence_level, n_iterations, sd)
    assert_almost_equal(result, precision, decimal=2)


EXPECTED_FLATTENED = {
    "value": [5],
    "sd": [2.581989],
    "min": [1],
    "max": [9],
    "statsDefinition": "simulated",
    "observations": [9]
}

EXPECTED_COLUMNWISE = {
    "value": [4, 5, 6],
    "sd": [2.44949, 2.44949, 2.44949],
    "min": [1, 2, 3],
    "max": [7, 8, 9],
    "statsDefinition": "simulated",
    "observations": [3, 3, 3]
}

EXPECTED_ROWWISE = {
    "value": [2, 5, 8],
    "sd": [0.816497, 0.816497, 0.816497],
    "min": [1, 4, 7],
    "max": [3, 6, 9],
    "statsDefinition": "simulated",
    "observations": [3, 3, 3]
}


@mark.parametrize(
    "axis, expected",
    [(None, EXPECTED_FLATTENED), (0, EXPECTED_COLUMNWISE), (1, EXPECTED_ROWWISE)],
    ids=["flattened", "columnwise", "rowwise"]
)
@mark.parametrize("stats_definition", [MeasurementStatsDefinition.SIMULATED, "simulated"], ids=["Enum", "str"])
def test_calc_descriptive_stats(stats_definition, axis, expected):
    ARR = array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ])

    result = calc_descriptive_stats(ARR, stats_definition, axis=axis)
    assert result == expected
