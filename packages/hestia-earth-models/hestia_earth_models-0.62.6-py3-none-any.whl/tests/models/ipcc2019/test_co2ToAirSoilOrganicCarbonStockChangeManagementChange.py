from functools import reduce
import json
from os.path import isfile
from pytest import mark
from unittest.mock import patch

from hestia_earth.schema import EmissionMethodTier, MeasurementMethodClassification

from hestia_earth.models.ipcc2019.co2ToAirSoilOrganicCarbonStockChangeManagementChange import (
    calc_soc_stock_change, calc_soc_stock_change_emission, convert_c_to_co2, lerp_soc_stocks, MODEL, run, TERM_ID,
    SocStock, SocStockChange, SocStockChangeEmission
)

from tests.utils import fake_new_emission, fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

RUN_SCENARIOS = [
    ("no-overlapping-cycles", 3),
    ("overlapping-cycles", 4),
    ("complex-overlapping-cycles", 5),
    ("missing-measurement-dates", 3),
    ("no-organic-carbon-measurements", 1),               # Closes issue #700
    ("non-consecutive-organic-carbon-measurements", 1),  # Closes issue #827
    ("multiple-method-classifications", 5),              # Closes issue #764
    ("non-soil-based-gohac-system", 3),                  # Closes issue #848
    ("soil-based-gohac-system", 3)                       # Closes issue #848
]
"""List of (subfolder: str, num_cycles: int)."""


def _load_fixture(path: str, default=None):
    if isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


RUN_PARAMS = reduce(
    lambda params, scenario: params + [(scenario[0], scenario[1], i) for i in range(scenario[1])],
    RUN_SCENARIOS,
    list()
)
"""List of (subfolder: str, num_cycles: int, cycle_index: int)."""

RUN_IDS = [f"{param[0]}, cycle{param[2]}" for param in RUN_PARAMS]


@mark.parametrize("subfolder, num_cycles, cycle_index", RUN_PARAMS, ids=RUN_IDS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}._get_site")
def test_run(_get_site_mock, related_cycles_mock, _new_emission_mock, subfolder, num_cycles, cycle_index):
    """
    Test `run` function for each cycle in each scenario.
    """
    site = _load_fixture(f"{fixtures_folder}/{subfolder}/site.jsonld")
    cycle = _load_fixture(f"{fixtures_folder}/{subfolder}/cycle{cycle_index}.jsonld")
    expected = _load_fixture(f"{fixtures_folder}/{subfolder}/result{cycle_index}.jsonld", default=[])

    cycles = [
        _load_fixture(f"{fixtures_folder}/{subfolder}/cycle{i}.jsonld") for i in range(num_cycles)
    ]

    _get_site_mock.return_value = site
    related_cycles_mock.return_value = cycles

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}._get_site")
def test_run_empty(_get_site_mock, related_cycles_mock, _new_emission_mock):
    """
    Test `run` function for each cycle in each scenario.
    """
    CYCLE = {}
    EXPECTED = []

    _get_site_mock.return_value = {}
    related_cycles_mock.return_value = [CYCLE]

    result = run(CYCLE)
    assert result == EXPECTED


def test_convert_c_to_co2():
    KG_C = 1000
    EXPECTED = 3663.836163836164
    assert convert_c_to_co2(KG_C) == EXPECTED


def test_linear_interpolate_soc_stock():
    START = SocStock(20000, "2000-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END = SocStock(22000, "2002-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    TARGET_DATE = "2001-12-31"
    EXPECTED = SocStock(21000, "2001-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)

    result = lerp_soc_stocks(START, END, TARGET_DATE)
    assert result == EXPECTED


def test_calc_soc_stock_change():
    START = SocStock(20000, "2000", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END = SocStock(21000,  "2001", MeasurementMethodClassification.TIER_1_MODEL)
    EXPECTED = SocStockChange(1000, "2000", "2001", MeasurementMethodClassification.TIER_1_MODEL)

    result = calc_soc_stock_change(START, END)
    assert result == EXPECTED


def test_calc_soc_stock_change_emission():
    SOC_STOCK_CHANGE = SocStockChange(-1000, "2000", "2001", MeasurementMethodClassification.TIER_1_MODEL)
    EXPECTED = SocStockChangeEmission(3663.836163836164, "2000", "2001", EmissionMethodTier.TIER_1)

    result = calc_soc_stock_change_emission(SOC_STOCK_CHANGE)
    assert result == EXPECTED
