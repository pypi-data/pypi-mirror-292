from hestia_earth.schema import MeasurementMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import has_original_by_ids
from hestia_earth.models.utils.measurement import SOIL_TEXTURE_IDS, _new_measurement
from hestia_earth.models.utils.source import get_source
from .utils import download, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ],
        "none": {
            "measurements": [{
                "@type": "Measurement",
                "term.@id": [
                    "clayContent",
                    "sandContent",
                    "siltContent"
                ]
            }]
        }
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": "geospatial dataset"
    }]
}
TERM_ID = 'clayContent'
EE_PARAMS = {
    'collection': 'T_CLAY',
    'ee_type': 'raster',
    'reducer': 'mean'
}
BIBLIO_TITLE = 'Harmonized World Soil Database Version 1.2. Food and Agriculture Organization of the United Nations (FAO).'  # noqa: E501


def _measurement(site: dict, value: int):
    measurement = _new_measurement(TERM_ID, None)
    measurement['value'] = [value]
    measurement['depthUpper'] = 0
    measurement['depthLower'] = 30
    measurement['methodClassification'] = MeasurementMethodClassification.GEOSPATIAL_DATASET.value
    return measurement | get_source(site, BIBLIO_TITLE)


def _download(site: dict):
    value = download(TERM_ID, site, EE_PARAMS)
    return None if value is None else round(value, 2)


def _run(site: dict):
    value = _download(site)
    return [_measurement(site, value)] if value is not None else []


def _should_run(site: dict):
    contains_geospatial_data = has_geospatial_data(site)
    below_max_area_size = should_download(TERM_ID, site)
    has_original_texture_measurements = has_original_by_ids(site.get('measurements', []), SOIL_TEXTURE_IDS)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    contains_geospatial_data=contains_geospatial_data,
                    below_max_area_size=below_max_area_size,
                    has_original_texture_measurements=has_original_texture_measurements)

    should_run = all([contains_geospatial_data, below_max_area_size, not has_original_texture_measurements])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
