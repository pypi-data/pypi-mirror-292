"""
Cycle Pasture Grass

This model estimates the energetic requirements of ruminants and can be used to estimate the amount of grass they graze.
Source:
[IPCC 2019, Vol.4, Chapter 10](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch10_Livestock.pdf).

This version of the model will run at the Cycle level, if at least one Cycle Input is given as feed
(see https://www.hestia.earth/schema/Input#isAnimalFeed).
"""
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.blank_node import lookups_logs, properties_logs
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.term import get_wool_terms
from hestia_earth.models.utils.completeness import _is_term_type_complete, _is_term_type_incomplete
from hestia_earth.models.utils.cycle import get_animals_by_period
from . import MODEL
from .pastureGrass_utils import (
    practice_input_id,
    should_run_practice,
    calculate_meanDE,
    calculate_meanECHHV,
    calculate_REM,
    calculate_REG,
    calculate_NEfeed,
    calculate_GE,
    product_wool_energy,
    get_animal_values
)

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.animalPopulation": "True",
        "completeness.freshForage": "False",
        "site": {
            "@type": "Site",
            "siteType": "permanent pasture"
        },
        "practices": [{
            "@type": "Practice",
            "value": "",
            "term.@id": "pastureGrass",
            "key": {
                "@type": "Term",
                "term.termType": "landCover"
            }
        }],
        "inputs": [{
            "@type": "Input",
            "term.units": "kg",
            "value": "> 0",
            "isAnimalFeed": "True",
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                }]
            }
        }],
        "animals": [{
            "@type": "Animal",
            "value": "> 0",
            "term.termType": "liveAnimal",
            "referencePeriod": "average",
            "properties": [{
                "@type": "Property",
                "value": "",
                "term.@id": [
                    "liveweightPerHead",
                    "weightAtMaturity"
                ]
            }],
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": [
                        "hoursWorkedPerDay",
                        "pregnancyRateTotal",
                        "animalsPerBirth"
                    ]
                }],
                "inputs": [{
                    "@type": "Input",
                    "term.units": "kg",
                    "value": "> 0",
                    "optional": {
                        "properties": [{
                            "@type": "Property",
                            "value": "",
                            "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                        }]
                    }
                }],
                "practices": [{
                    "@type": "Practice",
                    "value": "",
                    "term.termType": "animalManagement",
                    "properties": [{
                        "@type": "Property",
                        "value": "",
                        "term.@id": "fatContent"
                    }]
                }]
            }
        }],
        "optional": {
            "products": [{
                "@type": "Product",
                "value": "",
                "term.@id": "animalProduct"
            }]
        }
    }
}
LOOKUPS = {
    "animalManagement": [
        "mjKgEvMilkIpcc2019",
        "defaultFatContentEvMilkIpcc2019"
    ],
    "animalProduct": ["mjKgEvWoolNetEnergyWoolIpcc2019"],
    "liveAnimal": [
        "ipcc2019AnimalTypeGrouping",
        "mjDayKgCfiNetEnergyMaintenanceIpcc2019",
        "ratioCPregnancyNetEnergyPregnancyIpcc2019",
        "ratioCNetEnergyGrowthCattleBuffaloIpcc2019",
        "mjKgABNetEnergyGrowthSheepGoatsIpcc2019",
        "isWoolProducingAnimal"
    ],
    "system-liveAnimal-activityCoefficient-ipcc2019": "using animal term @id",
    "crop-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "crop": "grazedPastureGrassInputId",
    "forage-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "landCover": "grazedPastureGrassInputId"
}
RETURNS = {
    "Input": [{
        "term.termType": ["crop", "forage"],
        "value": ""
    }]
}
MODEL_KEY = 'pastureGrass'


def _input(term_id: str, value: float):
    node = _new_input(term_id, MODEL)
    node['value'] = [value]
    return node


def calculate_NEwool(cycle: dict) -> float:
    term_ids = get_wool_terms()
    products = [p for p in cycle.get('products', []) if p.get('term', {}).get('@id') in term_ids]
    product_values = [
        (list_sum(p.get('value', [])), product_wool_energy(p)) for p in products
    ]
    return sum([value * lookup_value for (value, lookup_value) in product_values])


def _run_practice(cycle: dict, meanDE: float, meanECHHV: float, system: dict):
    animals = get_animals_by_period(cycle)
    REM = calculate_REM(meanDE)
    REG = calculate_REG(meanDE)
    NEwool = calculate_NEwool(cycle)
    NEm_feed, NEg_feed = calculate_NEfeed(cycle)

    animal_values = [{
        'animalId': animal.get('term', {}).get('@id')
    } | get_animal_values(cycle, animal, system) for animal in animals]

    GE = (
        calculate_GE(animal_values, REM, REG, NEwool, NEm_feed, NEg_feed) / (meanDE/100)
    ) if meanDE else 0

    def run(practice: dict):
        key = practice.get('key', {})
        key_id = key.get('@id')
        input_term_id = practice_input_id(practice)
        value = (GE / meanECHHV) * (list_sum(practice.get('value', [0])) / 100)

        logs = log_as_table([v | {
            'practiceKeyId': key_id,
            'REM': REM,
            'REG': REG,
            'NEwool': NEwool,
            'NEmFeed': NEm_feed,
            'NEgFeed': NEg_feed,
            'GE': GE,
            'meanECHHV': meanECHHV,
            'meanDE': meanDE
        } for v in animal_values])
        animal_lookups = lookups_logs(MODEL, animals, LOOKUPS, model_key=MODEL_KEY, term=input_term_id)
        animal_properties = properties_logs(animals, properties=[
            'liveweightPerHead',
            'hoursWorkedPerDay',
            'animalsPerBirth',
            'pregnancyRateTotal',
            'weightAtMaturity',
            'liveweightGain',
            'weightAtWeaning',
            'weightAtOneYear',
            'weightAtSlaughter'
        ])

        logRequirements(cycle, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        animal_logs=logs,
                        animal_lookups=animal_lookups,
                        animal_properties=animal_properties)

        logShouldRun(cycle, MODEL, input_term_id, True, model_key=MODEL_KEY)

        return _input(input_term_id, value)

    return run


def _should_run(cycle: dict, practices: dict):
    systems = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM)
    animalFeed_complete = _is_term_type_complete(cycle, 'animalFeed')
    animalPopulation_complete = _is_term_type_complete(cycle, 'animalPopulation')
    freshForage_incomplete = _is_term_type_incomplete(cycle, 'freshForage')
    all_animals_have_value = all([a.get('value', 0) > 0 for a in cycle.get('animals', [])])

    has_cycle_inputs_feed = any([i.get('isAnimalFeed', False) for i in cycle.get('inputs', [])])

    meanDE = calculate_meanDE(practices)
    meanECHHV = calculate_meanECHHV(practices)

    should_run = all([
        animalFeed_complete,
        animalPopulation_complete,
        freshForage_incomplete,
        has_cycle_inputs_feed,
        all_animals_have_value,
        len(systems) > 0,
        len(practices) > 0,
        meanDE > 0,
        meanECHHV > 0
    ])

    for term_id in [practice_input_id(p) for p in practices] or [MODEL_KEY]:
        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        term_type_animalFeed_complete=animalFeed_complete,
                        term_type_animalPopulation_complete=animalPopulation_complete,
                        term_type_freshForage_incomplete=freshForage_incomplete,
                        has_cycle_inputs_feed=has_cycle_inputs_feed,
                        all_animals_have_value=all_animals_have_value,
                        meanDE=calculate_meanDE(practices, term=term_id),
                        meanECHHV=calculate_meanECHHV(practices, term=term_id))

        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    return should_run, meanDE, meanECHHV, systems[0] if systems else None


def run(cycle: dict):
    practices = list(filter(should_run_practice(cycle), cycle.get('practices', [])))
    should_run, meanDE, meanECHHV, system = _should_run(cycle, practices)
    return list(map(_run_practice(cycle, meanDE, meanECHHV, system), practices)) if should_run else []
