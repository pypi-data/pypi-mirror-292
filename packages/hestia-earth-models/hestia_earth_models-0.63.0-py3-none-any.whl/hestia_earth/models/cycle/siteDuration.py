"""
Site duration

This model calculates the `siteDuration` on the `Cycle` to the same value as `cycleDuration`
when only a single `Site` is present.

Note: on `crop` production cycles, the model will only run if `startDateDefinition` = `harvest of previous crop`.
"""
from hestia_earth.schema import TermTermType, CycleStartDateDefinition
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logRequirements, logShouldRun
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "> 0",
        "none": {
            "otherSites": ""
        },
        "optional": {
            "products": {
                "@type": "Product",
                "primary": "True",
                "term.termType": "crop"
            },
            "startDateDefinition": ""
        }
    }
}
RETURNS = {
    "the duration as a `number`": ""
}
MODEL_KEY = 'siteDuration'


def _run(cycle: dict): return cycle.get('cycleDuration')


def _should_run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 0)
    has_other_sites = len(cycle.get('otherSites', [])) == 0

    product = find_primary_product(cycle)
    is_primary_crop_product = (product or {}).get('term', {}).get('termType') == TermTermType.CROP.value
    harvest_previous_crop = CycleStartDateDefinition.HARVEST_OF_PREVIOUS_CROP.value
    is_harvest_previous_crop = cycle.get('startDateDefinition') == harvest_previous_crop

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    cycleDuration=cycleDuration,
                    has_other_sites=has_other_sites,
                    is_primary_crop_product=is_primary_crop_product,
                    is_harvest_previous_crop=is_harvest_previous_crop)

    should_run = all([cycleDuration > 0, has_other_sites, not is_primary_crop_product or is_harvest_previous_crop])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else None
