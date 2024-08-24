from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from functools import reduce
from itertools import product
from pydash.objects import merge
from typing import NamedTuple, Optional, Union

from hestia_earth.schema import (
    CycleFunctionalUnit, EmissionMethodTier, MeasurementMethodClassification, SiteSiteType
)
from hestia_earth.utils.date import diff_in_days
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_date

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils import pairwise
from hestia_earth.models.utils.blank_node import (
    _get_datestr_format, _gapfill_datestr, DatestrGapfillMode, DatestrFormat, group_nodes_by_year, node_term_match,
    cumulative_nodes_term_match
)
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission, min_emission_method_tier
from hestia_earth.models.utils.measurement import (
    group_measurements_by_method_classification, min_measurement_method_classification,
    to_measurement_method_classification
)
from hestia_earth.models.utils.site import related_cycles

from .utils import check_consecutive
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "measurements": [
                {
                    "@type": "Measurement",
                    "value": "",
                    "dates": "",
                    "depthUpper": "0",
                    "depthLower": "30",
                    "term.@id": " organicCarbonPerHa"
                }
            ]
        },
        "functionalUnit": "1 ha",
        "endDate": "",
        "optional": {
            "startDate": ""
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "",
        "depth": "30"
    }]
}
TERM_ID = 'co2ToAirSoilOrganicCarbonStockChangeManagementChange'

DEPTH_UPPER = 0
DEPTH_LOWER = 30

ORGANIC_CARBON_PER_HA_TERM_ID = 'organicCarbonPerHa'

VALID_DATE_FORMATS = {
    DatestrFormat.YEAR,
    DatestrFormat.YEAR_MONTH,
    DatestrFormat.YEAR_MONTH_DAY,
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
}

VALID_MEASUREMENT_METHOD_CLASSIFICATIONS = [
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
    MeasurementMethodClassification.TIER_3_MODEL,
    MeasurementMethodClassification.TIER_2_MODEL,
    MeasurementMethodClassification.TIER_1_MODEL
]
"""
The list of `MeasurementMethodClassification`s that can be used to calculate SOC stock change emissions, ranked in
order from strongest to weakest.
"""

_SITE_TYPE_SYSTEMS_MAPPING = {
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value: [
        "protectedCroppingSystemSoilBased",
        "protectedCroppingSystemSoilAndSubstrateBased"
    ]
}


class _InventoryKey(Enum):
    """
    The inner keys of the annualised inventory created by the `_compile_inventory` function.

    The value of each enum member is formatted to be used as a column header in the `log_as_table` function.
    """
    SOC_STOCK = "soc-stock"
    SOC_STOCK_CHANGE = "soc-stock-change"
    CO2_EMISSION = "co2-emission"
    SHARE_OF_EMISSION = "share-of-emissions"


SocStock = NamedTuple("SocStock", [
    ("value", float),
    ("date", str),
    ("method", MeasurementMethodClassification)
])
"""
NamedTuple representing an SOC stock.

Attributes
----------
value : float
    The value of the SOC stock (kg C ha-1).
date : str
    The date of the measurement as a datestr with format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The measurement method for the SOC stock.
"""

SocStockChange = NamedTuple("SocStockChange", [
    ("value", float),
    ("start_date", str),
    ("end_date", str),
    ("method", MeasurementMethodClassification)
])
"""
NamedTuple representing an SOC stock change.

Attributes
----------
value : float
    The value of the SOC stock change (kg C ha-1).
start_date : str
    The start date of the SOC stock change event as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
end_date : str
    The end date of the SOC stock change event as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The measurement method for the SOC stock change.
"""

SocStockChangeEmission = NamedTuple("SocStockChangeEmission", [
    ("value", float),
    ("start_date", str),
    ("end_date", str),
    ("method", EmissionMethodTier)
])
"""
NamedTuple representing an SOC stock change emission.

Attributes
----------
value : float
    The value of the SOC stock change (kg CO2 ha-1).
start_date : str
    The start date of the SOC stock change emission as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
end_date : str
    The end date of the SOC stock change emission as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The emission method tier.
"""


def _emission(value: float, method_tier: EmissionMethodTier) -> dict:
    """
    Create an emission node based on the provided value and method tier.

    See [Emission schema](https://www.hestia.earth/schema/Emission) for more information.

    Parameters
    ----------
    value : float
        The emission value (kg CO2 ha-1).

    method_tier : EmissionMethodTier
        The emission method tier.

    Returns
    -------
    dict
        The emission dictionary with keys 'depth', 'value', and 'methodTier'.
    """
    emission = _new_emission(TERM_ID, MODEL)
    emission["depth"] = DEPTH_LOWER
    emission["value"] = [value]
    emission["methodTier"] = method_tier.value
    return emission


def _should_run(cycle: dict) -> tuple[bool, str, dict]:
    """
    Determine if calculations should run for a given [Cycle](https://www.hestia.earth/schema/Cycle) based on SOC stock
    and emissions data.

    Parameters
    ----------
    cycle : dict
        The cycle dictionary for which the calculations will be evaluated.

    Returns
    -------
    tuple[bool, str, dict]
        `(should_run, cycle_id, inventory)`
    """
    cycle_id = cycle.get("@id")
    site = _get_site(cycle)
    soc_measurements = [node for node in site.get("measurements", []) if _validate_soc_measurement(node)]
    cycles = related_cycles(site)

    site_type = site.get("siteType")
    has_soil = site_type not in _SITE_TYPE_SYSTEMS_MAPPING or all(
        cumulative_nodes_term_match(
            cycle.get("practices", []),
            target_term_ids=_SITE_TYPE_SYSTEMS_MAPPING[site_type],
            cumulative_threshold=0
        ) for cycle in cycles
    )

    has_soc_measurements = len(soc_measurements) > 0
    has_cycles = len(cycles) > 0
    has_functional_unit_1_ha = all(cycle.get('functionalUnit') == CycleFunctionalUnit._1_HA.value for cycle in cycles)

    should_compile_inventory = all([
        has_soil,
        has_cycles,
        has_functional_unit_1_ha,
        has_soc_measurements,
    ])

    inventory, logs = (
        _compile_inventory(cycle_id, cycles, soc_measurements) if should_compile_inventory else ({}, {})
    )

    has_valid_inventory = len(inventory) > 0
    has_consecutive_years = check_consecutive(inventory.keys())

    logRequirements(
        cycle, model=MODEL, term=TERM_ID,
        site_type=site_type,
        has_soil=has_soil,
        has_soc_measurements=has_soc_measurements,
        has_cycles=has_cycles,
        has_functional_unit_1_ha=has_functional_unit_1_ha,
        has_valid_inventory=has_valid_inventory,
        has_consecutive_years=has_consecutive_years,
        **logs
    )

    should_run = all([has_valid_inventory, has_consecutive_years])

    logShouldRun(cycle, MODEL, TERM_ID, should_run)

    return should_run, cycle_id, inventory


def _get_site(cycle: dict) -> dict:
    """
    Get the [Site](https://www.hestia.earth/schema/Site) data from a [Cycle](https://www.hestia.earth/schema/Cycle).

    Parameters
    ----------
    cycle : dict

    Returns
    -------
    str
    """
    return cycle.get("site", {})


def _validate_soc_measurement(node: dict) -> bool:
    """
    Validate a [Measurement](https://www.hestia.earth/schema/Measurement) to determine whether it is a valid
    `organicCarbonPerHa` node.

    Parameters
    ----------
    node : dict
        The node to be validated.

    Returns
    -------
    bool
        `True` if the node passes all validation criteria, `False` otherwise.
    """
    value = node.get("value", [])
    dates = node.get("dates", [])
    return all([
        node_term_match(node, ORGANIC_CARBON_PER_HA_TERM_ID),
        node.get("depthUpper") == DEPTH_UPPER,
        node.get("depthLower") == DEPTH_LOWER,
        node.get("methodClassification") in (m.value for m in VALID_MEASUREMENT_METHOD_CLASSIFICATIONS),
        len(value) > 0,
        len(value) == len(dates),
        all(_get_datestr_format(datestr) in VALID_DATE_FORMATS for datestr in dates)
    ])


def _compile_inventory(cycle_id: str, cycles: list[dict], soc_measurements: list[dict]) -> tuple[dict, dict]:
    """
    Compile an annual inventory of SOC stocks, SOC stock changes, SOC stock change emissions and the share of emissions
    of cycles.

    A separate inventory is compiled for each valid `MeasurementMethodClassification` present in the input data, which
    are then merged together by selecting the strongest available method for each relevant inventory year.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.SOC_STOCK: value (SocStock),
            _InventoryKey.SOC_STOCK_CHANGE: value (SocStockChange),
            _InventoryKey.CO2_EMISSION: value (SocStockChangeEmission),
            _InventoryKey.SHARE_OF_EMISSION: {
                cycle_id (str): value (float),
                ...cycle_ids
            }
        },
        ...years
    }
    ```

    Parameters
    ----------
    cycle_id : str
    cycles : list[dict]
    soc_measurements: list[dict]

    Returns
    -------
    tuple[dict, dict]
        `(inventory, logs)`
    """
    cycle_inventory = _compile_cycle_inventory(cycles)

    soc_measurements_by_method = group_measurements_by_method_classification(soc_measurements)
    soc_inventory = {
        method: _compile_soc_inventory(soc_measurements)
        for method, soc_measurements in soc_measurements_by_method.items()
    }

    logs = {
        "cycle_inventory": _format_cycle_inventory(cycle_inventory),
        "soc_inventory": _format_soc_inventory(soc_inventory)
    }

    inventory = _squash_inventory(cycle_id, cycle_inventory, soc_inventory)
    return inventory, logs


def _compile_cycle_inventory(cycles: list[dict]) -> dict:
    """
    Calculate grouped share of emissions for cycles based on the amount they contribute the the overall land management
    of an inventory year.

    This function groups cycles by year, then calculates the share of emissions for each cycle based on the
    "fraction_of_group_duration" value. The share of emissions is normalized by the sum of cycle occupancies for the
    entire dataset to ensure the values represent a valid share.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.SHARE_OF_EMISSION: {
                cycle_id (str): value (float),
                ...cycle_ids
            }
        },
        ...years
    }
    ```

    Parameters
    ----------
    cycles : list[dict]
        List of [Cycle nodes](https://www.hestia.earth/schema/Cycle), where each cycle dictionary should contain a
        "fraction_of_group_duration" key added by the `group_nodes_by_year` function.

    Returns
    -------
    dict
        A dictionary with grouped share of emissions for each cycle based on the fraction of the year.
    """
    grouped_cycles = group_nodes_by_year(cycles)
    return {
        year: {
            _InventoryKey.SHARE_OF_EMISSION: {
                cycle["@id"]: (
                    cycle.get("fraction_of_group_duration", 0)
                    / sum(cycle.get("fraction_of_group_duration", 0) for cycle in cycles)
                ) for cycle in cycles
            }
        } for year, cycles in grouped_cycles.items()
    }


def _compile_soc_inventory(soc_measurements: list[dict]) -> dict:
    """
    Compile an annual inventory of SOC stock data and pre-computed SOC stock change emissions.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.SOC_STOCK: value (SocStock),
            _InventoryKey.SOC_STOCK_CHANGE: value (SocStockChange),
            _InventoryKey.CO2_EMISSION: value (SocStockChangeEmission)
        },
        ...years
    }
    ```

    Parameters
    ----------
    soc_measurements : list[dict]
        List of pre-validated `organicCarbonPerHa` [Measurement nodes](https://www.hestia.earth/schema/Measurement).

    Returns
    -------
    dict
        The annual inventory.
    """

    values = flatten(measurement.get("value", []) for measurement in soc_measurements)
    dates = flatten(
        [_gapfill_datestr(datestr, DatestrGapfillMode.END) for datestr in measurement.get("dates", [])]
        for measurement in soc_measurements
    )
    methods = flatten(
        [MeasurementMethodClassification(measurement.get("methodClassification")) for _ in measurement.get("value", [])]
        for measurement in soc_measurements
    )

    soc_stocks = sorted(
        [SocStock(value, datestr, method) for value, datestr, method in zip(values, dates, methods)],
        key=lambda soc_stock: soc_stock.date
    )

    def interpolate_between(result: dict, soc_stock_pair: tuple[SocStock, SocStock]) -> dict:
        start, end = soc_stock_pair[0], soc_stock_pair[1]

        start_date = safe_parse_date(start.date, datetime.min)
        end_date = safe_parse_date(end.date, datetime.min)

        should_run = (
            datetime.min != start_date != end_date
            and end_date > start_date
        )

        update = {
            year: {_InventoryKey.SOC_STOCK: lerp_soc_stocks(start, end, f"{year}-12-31T23:59:59")}
            for year in range(start_date.year, end_date.year+1)
        } if should_run else {}

        return result | update

    soc_stocks_by_year = reduce(interpolate_between, pairwise(soc_stocks), dict())

    soc_stock_changes_by_year = {
        year: {
            _InventoryKey.SOC_STOCK_CHANGE: calc_soc_stock_change(
                start_group[_InventoryKey.SOC_STOCK],
                end_group[_InventoryKey.SOC_STOCK]
            )
        } for (_, start_group), (year, end_group) in pairwise(soc_stocks_by_year.items())
    }

    co2_emissions_by_method_and_year = {
        year: {
            _InventoryKey.CO2_EMISSION: calc_soc_stock_change_emission(
                group[_InventoryKey.SOC_STOCK_CHANGE]
            )
        } for year, group in soc_stock_changes_by_year.items()
    }

    return _sorted_merge(soc_stocks_by_year, soc_stock_changes_by_year, co2_emissions_by_method_and_year)


def lerp_soc_stocks(start: SocStock, end: SocStock, target_date: str) -> SocStock:
    """
    Estimate, using linear interpolation, an SOC stock for a specific date based on the the SOC stocks of two other
    dates.

    Parameters
    ----------
    start : SocStock
        The `SocStock` at the start (kg C ha-1).
    end : SocStock
        The `SocStock` at the end (kg C ha-1).
    target_date : str
        The target date for interpolation as a datestr with format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.

    Returns
    -------
    SocStock
        The interpolated `SocStock` for the specified date (kg C ha-1).
    """
    time_ratio = diff_in_days(start.date, target_date) / diff_in_days(start.date, end.date)
    soc_delta = (end.value - start.value) * time_ratio

    value = start.value + soc_delta
    method = min_measurement_method_classification(start.method, end.method)

    return SocStock(value, target_date, method)


def calc_soc_stock_change(start: SocStock, end: SocStock) -> SocStockChange:
    """
    Calculate the change in SOC stock change between the current and previous states.

    The method should be the weaker of the two `MeasurementMethodClassification`s.

    Parameters
    ----------
    start : SocStock
        The SOC stock at the start (kg C ha-1).

    end : SocStock
        The SOC stock at the end (kg C ha-1).

    Returns
    -------
    SocStockChange
        The SOC stock change (kg C ha-1).
    """
    value = end.value - start.value
    method = min_measurement_method_classification(start.method, end.method)
    return SocStockChange(value, start.date, end.date, method)


def calc_soc_stock_change_emission(soc_stock_change: SocStockChange) -> SocStockChangeEmission:
    """
    Convert an `SocStockChange` into an `SocStockChangeEmission`.

    Parameters
    ----------
    soc_stock_change : SocStockChange
        The SOC stock at the start (kg C ha-1).

    Returns
    -------
    SocStockChangeEmission
        The SOC stock change emission (kg CO2 ha-1).
    """
    value = convert_c_to_co2(soc_stock_change.value) * -1
    method = convert_mmc_to_emt(soc_stock_change.method)
    return SocStockChangeEmission(value, soc_stock_change.start_date, soc_stock_change.end_date, method)


_DEFAULT_EMISSION_METHOD_TIER = EmissionMethodTier.TIER_1
_MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER = {
    MeasurementMethodClassification.TIER_2_MODEL: EmissionMethodTier.TIER_2,
    MeasurementMethodClassification.TIER_3_MODEL: EmissionMethodTier.TIER_3,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS: EmissionMethodTier.MEASURED,
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT: EmissionMethodTier.MEASURED,
}
"""
A mapping between `MeasurementMethodClassification`s and `EmissionMethodTier`s. As SOC measurements can be
measured/estimated through a variety of methods, the emission model needs be able to assign an emission tier for each.
Any `MeasurementMethodClassification` not in the mapping should be assigned `DEFAULT_EMISSION_METHOD_TIER`.
"""


def convert_mmc_to_emt(
    measurement_method_classification: MeasurementMethodClassification
) -> EmissionMethodTier:
    """
    Get the emission method tier based on the provided measurement method classification.

    Parameters
    ----------
    measurement_method : MeasurementMethodClassification
        The measurement method classification.

    Returns
    -------
    EmissionMethodTier
        The corresponding emission method tier.
    """
    return _MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER.get(
        to_measurement_method_classification(measurement_method_classification),
        _DEFAULT_EMISSION_METHOD_TIER
    )


def convert_c_to_co2(kg_c: float) -> float:
    """
    Convert mass of carbon (C) to carbon dioxide (CO2) using the atomic conversion ratio.

    n.b. `get_atomic_conversion` returns the ratio C:CO2 (~44/12).

    Parameters
    ----------
    kg_c : float
        Mass of carbon (C) to be converted to carbon dioxide (CO2) (kg C).

    Returns
    -------
    float
        Mass of carbon dioxide (CO2) resulting from the conversion (kg CO2).
    """
    return kg_c * get_atomic_conversion(Units.KG_CO2, Units.TO_C)


def _sorted_merge(*sources: Union[dict, list[dict]]) -> dict:
    """
    Merge dictionaries and return the result as a new dictionary with keys sorted in order to preserve the temporal
    order of inventory years.

    Parameters
    ----------
    *sources : dict | list[dict]
        One or more dictionaries or lists of dictionaries to be merged.

    Returns
    -------
    dict
        A new dictionary containing the merged key-value pairs, with keys sorted.
    """

    _sources = non_empty_list(
        flatten([arg if isinstance(arg, list) else [arg] for arg in sources])
    )

    merged = reduce(merge, _sources, {})
    return dict(sorted(merged.items()))


def _squash_inventory(cycle_id: str, cycle_inventory: dict, soc_inventory: dict) -> dict:
    """
    Merge the `cycle_inventory` and `soc_inventory` for each inventory year by selecting the strongest available
    `MeasurementMethodClassification`. Years that do not overlap with the Cycle node that the emission model is running
    on should be discarded as they are not relevant.

    Parameters
    ----------
    cycle_id : str
    cycle_inventory : dict
    soc_inventory: dict

    Returns
    -------
    dict
        The squashed inventory.
    """
    inventory_years = sorted(set(non_empty_list(
        flatten(list(years) for years in soc_inventory.values())
        + list(cycle_inventory.keys())
    )))

    def should_run_group(method: MeasurementMethodClassification, year: int) -> bool:
        soc_stock_inventory_group = soc_inventory.get(method, {}).get(year, {})
        share_of_emissions_group = cycle_inventory.get(year, {})

        has_emission = _InventoryKey.CO2_EMISSION in soc_stock_inventory_group.keys()
        is_relevant_for_cycle = cycle_id in share_of_emissions_group.get(_InventoryKey.SHARE_OF_EMISSION, {}).keys()
        return all([has_emission, is_relevant_for_cycle])

    def squash(result: dict, year: int) -> dict:
        update_dict = next(
            (
                {year: reduce(merge, [soc_inventory[method][year], cycle_inventory[year]], dict())}
                for method in VALID_MEASUREMENT_METHOD_CLASSIFICATIONS if should_run_group(method, year)
            ),
            {}
        )
        return result | update_dict

    return reduce(squash, inventory_years, dict())


def _format_cycle_inventory(cycle_inventory: dict) -> str:
    """
    Format the cycle inventory for logging as a table. Rows represent inventory years, columns represent the share of
    emission for each cycle present in the inventory. If the inventory is invalid, return `"None"` as a string.
    """
    KEY = _InventoryKey.SHARE_OF_EMISSION

    unique_cycles = sorted(
        set(non_empty_list(flatten(list(group[KEY]) for group in cycle_inventory.values()))),
        key=lambda id: next((year, id) for year in cycle_inventory if id in cycle_inventory[year][KEY])
    )

    should_run = cycle_inventory and len(unique_cycles) > 0

    return log_as_table(
        {
            "year": year,
            **{
                id: _format_number(group.get(KEY, {}).get(id, 0)) for id in unique_cycles
            }
        } for year, group in cycle_inventory.items()
    ) if should_run else "None"


def _format_soc_inventory(soc_inventory: dict) -> str:
    """
    Format the SOC inventory for logging as a table. Rows represent inventory years, columns represent soc stock change
    data for each measurement method classification present in inventory. If the inventory is invalid, return `"None"`
    as a string.
    """
    KEYS = [
        _InventoryKey.SOC_STOCK,
        _InventoryKey.SOC_STOCK_CHANGE,
        _InventoryKey.CO2_EMISSION
    ]

    methods = soc_inventory.keys()
    method_columns = list(product(methods, KEYS))
    inventory_years = sorted(set(non_empty_list(flatten(list(years) for years in soc_inventory.values()))))

    should_run = soc_inventory and len(inventory_years) > 0

    return log_as_table(
        {
            "year": year,
            **{
                _format_column_header(method, key): _format_named_tuple(
                    soc_inventory.get(method, {}).get(year, {}).get(key, {})
                ) for method, key in method_columns
            }
        } for year in inventory_years
    ) if should_run else "None"


def _format_number(value: Optional[float]) -> str:
    """Format a float for logging in a table. If the value is invalid, return `"None"` as a string."""
    return f"{value:.1f}" if isinstance(value, (float, int)) else "None"


def _format_column_header(method: MeasurementMethodClassification, inventory_key: _InventoryKey) -> str:
    """
    Format a measurement method classification and inventory key for logging in a table as a column header. Replace any
    whitespaces in the method value with dashes and concatenate it with the inventory key value, which already has the
    correct format.
    """
    return "-".join([
        method.value.replace(" ", "-"),
        inventory_key.value
    ])


def _format_named_tuple(value: Optional[Union[SocStock, SocStockChange, SocStockChangeEmission]]) -> str:
    """
    Format a named tuple (`SocStock`, `SocStockChange` or `SocStockChangeEmission`) for logging in a table. Extract and
    format just the value and discard the other data. If the value is invalid, return `"None"` as a string.
    """
    return (
        _format_number(value.value)
        if isinstance(value, (SocStock, SocStockChange, SocStockChangeEmission))
        else "None"
    )


def _run(cycle_id: str, inventory: dict) -> list[dict]:
    """
    Calculate emissions for a specific cycle using grouped SOC stock change and share of emissions data.

    The emission method tier based on the minimum measurement method tier among the SOC stock change data in the
    grouped data.

    Parameters
    ----------
    cycle_id : str
        The "@id" field of the [Cycle node](https://www.hestia.earth/schema/Cycle).
    grouped_data : dict
        A dictionary containing grouped SOC stock change and share of emissions data.

    Returns
    -------
    list[dict]
        A list containing emission data calculated for the specified cycle.
    """
    total_emission = _sum_soc_stock_change_emissions([
        _rescale_stock_change_emission(
            group[_InventoryKey.CO2_EMISSION], group[_InventoryKey.SHARE_OF_EMISSION][cycle_id]
        ) for group in inventory.values()
    ])

    value = round(total_emission.value, 6)
    method_tier = total_emission.method
    return [_emission(value, method_tier)]


def _rescale_stock_change_emission(emission: SocStockChangeEmission, factor: float) -> SocStockChangeEmission:
    """
    Rescale an `SocStockChangeEmission` by a specified factor.

    Parameters
    ----------
    emission : SocStockChangeEmission
        An SOC stock change emission (kg CO2 ha-1).
    factor : float
        A scaling factor (e.g., a [Cycles](https://www.hestia.earth/schema/Cycle)'s share of an annual emission).

    Returns
    -------
    SocStockChangeEmission
        The rescaled emission.
    """
    value = emission.value * factor
    return SocStockChangeEmission(value, emission.start_date, emission.end_date, emission.method)


def _sum_soc_stock_change_emissions(emissions: Iterable[SocStockChangeEmission]) -> SocStockChangeEmission:
    """
    Sum together multiple `SocStockChangeEmission`s.

    Parameters
    ----------
    emissions : Iterable[SocStockChangeEmission]
        A list of SOC stock change emissions (kg CO2 ha-1).

    Returns
    -------
    SocStockChangeEmission
        The summed emission.
    """
    value = sum(e.value for e in emissions)
    start_date = min(e.start_date for e in emissions)
    end_date = max(e.end_date for e in emissions)
    method = min_emission_method_tier(e.method for e in emissions)

    return SocStockChangeEmission(value, start_date, end_date, method)


def run(cycle: dict) -> list[dict]:
    should_run, *args = _should_run(cycle)
    return _run(*args) if should_run else []
