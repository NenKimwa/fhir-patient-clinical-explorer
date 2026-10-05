import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clinical_analytics import (
    build_analytics,
    extract_observations,
    get_clinical_date,
    get_loinc_code,
    has_observation_value,
    get_observation_values,
    interpret_measurement,
)


def make_bundle():
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 5,
        "entry": [
            {"resource": {
                "resourceType": "Observation",
                "id": "18",
                "status": "final",
                "code": {"coding": [{
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel with all children optional"
                }]},
                "component": [
                    {"code": {"coding": [{
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure"
                    }]}, "valueQuantity": {"value": 120, "unit": "mmHg"}},
                    {"code": {"coding": [{
                        "system": "http://loinc.org",
                        "code": "8462-4",
                        "display": "Diastolic blood pressure"
                    }]}, "valueQuantity": {"value": 80, "unit": "mmHg"}},
                ],
            }},
            {"resource": {
                "resourceType": "Observation",
                "id": "52",
                "status": "final",
                "code": {"coding": [{
                    "system": "http://loinc.org",
                    "code": "4548-4",
                    "display": "Hemoglobin A1c/Hemoglobin.total in Blood"
                }]},
                "valueQuantity": {"value": 5.8, "unit": "%"},
            }},
            {"resource": {
                "resourceType": "Patient",
                "id": "17",
                "name": [{"given": ["Aisha"], "family": "Bello"}],
                "gender": "female",
                "birthDate": "1998-10-10",
            }},
            {"resource": {
                "resourceType": "Practitioner",
                "id": "19",
                "name": [{"given": ["Blessed"], "family": "Flourish"}],
            }},
            {"resource": {
                "resourceType": "Encounter",
                "id": "53",
                "status": "finished",
                "class": {"display": "ambulatory"},
            }},
        ],
    }


def test_extract_observations():
    observations = extract_observations(make_bundle())
    assert len(observations) == 2
    assert {o["id"] for o in observations} == {"18", "52"}


def test_build_analytics_counts():
    analytics = build_analytics(make_bundle())
    overview = analytics["observation_overview"]
    resources = analytics["resource_overview"]

    assert overview["total"] == 2
    assert overview["with_values"] == 2
    assert overview["without_values"] == 0
    assert overview["with_clinical_dates"] == 0
    assert overview["without_clinical_dates"] == 2
    assert resources["practitioners"] == 1
    assert resources["encounters"] == 1


def test_loinc_and_values():
    observations = [
        entry["resource"]
        for entry in make_bundle()["entry"]
        if entry["resource"]["resourceType"] == "Observation"
    ]
    bp, hba1c = observations

    assert get_loinc_code(bp) == "85354-9"
    assert has_observation_value(bp) is True
    assert get_observation_values(bp)[0]["value"] == 120
    assert get_loinc_code(hba1c) == "4548-4"
    assert has_observation_value(hba1c) is True
    assert get_observation_values(hba1c)[0]["value"] == 5.8


def test_clinical_date_support():
    assert get_clinical_date(
        {"effectiveDateTime": "2026-09-28T13:00:00Z"}
    ) == "2026-09-28T13:00:00Z"

    assert get_clinical_date({
        "effectivePeriod": {
            "start": "2026-09-28T13:00:00Z",
            "end": "2026-09-28T14:00:00Z",
        }
    }) == "2026-09-28T13:00:00Z"


def test_informational_interpretations():
    bp_values = [
        {"name": "Systolic blood pressure", "value": 120, "unit": "mmHg"},
        {"name": "Diastolic blood pressure", "value": 80, "unit": "mmHg"},
    ]
    assert interpret_measurement("Blood pressure panel", bp_values) == [
        "Diastolic blood pressure is at the upper end of the commonly used normal range."
    ]

    hba1c_values = [{"name": "Result", "value": 5.8, "unit": "%"}]
    assert interpret_measurement(
        "Hemoglobin A1c/Hemoglobin.total in Blood",
        hba1c_values,
    ) == ["Within the commonly used prediabetes range."]
