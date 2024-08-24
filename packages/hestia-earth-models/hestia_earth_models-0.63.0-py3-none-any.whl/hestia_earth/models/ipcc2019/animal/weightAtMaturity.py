"""
Note: when the `liveweightPerHead` property is provided, this model will only work if the returned value is
greater than or equal to `liveweightPerHead` value.
"""
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun, debugMissingLookup
from hestia_earth.models.utils.property import _new_property, node_has_no_property
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        },
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "none": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": "weightAtMaturity"
                }]
            },
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": "liveweightPerHead"
                }]
            }
        }]
    }
}
LOOKUPS = {
    "region-liveAnimal-weightAtMaturity": "weight at maturity"
}
RETURNS = {
    "Animal": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'weightAtMaturity'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _run_animal(data: dict):
    animal = data.get('animal')
    value = data.get('value')
    return animal | {
        'properties': animal.get('properties', []) + [_property(value)]
    }


def _lookup_value(country_id: str, animal: dict):
    lookup_name = f"{list(LOOKUPS.keys())[0]}.csv"
    lookup = download_lookup(lookup_name)
    column = column_name(animal.get('term').get('@id'))
    value = get_table_value(lookup, 'termid', country_id, column)
    debugMissingLookup(lookup_name, 'termid', country_id, column, value, model=MODEL, term=TERM_ID)
    return safe_parse_float(value)


def _should_run(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    live_animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    live_animals = list(filter(node_has_no_property(TERM_ID), live_animals))
    live_animals_with_value = [{'animal': a, 'value': _lookup_value(country_id, a)} for a in live_animals]

    def _should_run_animal(value: dict):
        lookup_value = value.get('value')
        term_id = value.get('animal').get('term').get('@id')
        liveweightPerHead = find_term_match(value.get('animal').get('properties', []), 'liveweightPerHead', {})
        liveweightPerHead_value = liveweightPerHead.get('value')

        logRequirements(cycle, model=MODEL, term=term_id,
                        country_id=country_id,
                        weightAtMaturity=lookup_value,
                        liveweightPerHead=liveweightPerHead_value)

        should_run = all([
            country_id,
            lookup_value is not None,
            lookup_value is None or liveweightPerHead_value is None or lookup_value >= liveweightPerHead_value
        ])
        logShouldRun(cycle, MODEL, term_id, should_run)

        return should_run

    return list(filter(_should_run_animal, live_animals_with_value))


def run(cycle: dict):
    animals = _should_run(cycle)
    return list(map(_run_animal, animals))
