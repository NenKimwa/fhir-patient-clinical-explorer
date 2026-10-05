import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clinical_report import build_clinical_report


def make_bundle():
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 5,
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "18",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "85354-9",
                            "display": "Blood pressure panel with all children optional"
                        }]
                    },
                    "component": [
                        {
                            "code": {"coding": [{
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }]},
                            "valueQuantity": {"value": 120, "unit": "mmHg"}
                        },
                        {
                            "code": {"coding": [{
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure"
                            }]},
                            "valueQuantity": {"value": 80, "unit": "mmHg"}
                        }
                    ]
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "52",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "4548-4",
                            "display": "Hemoglobin A1c/Hemoglobin.total in Blood"
                        }]
                    },
                    "valueQuantity": {"value": 5.8, "unit": "%"}
                }
            },
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "17",
                    "name": [{"given": ["Aisha"], "family": "Bello"}],
                    "gender": "female",
                    "birthDate": "1998-10-10"
                }
            },
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "19",
                    "name": [{"given": ["Blessed"], "family": "Flourish"}]
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "53",
                    "status": "finished",
                    "class": {"display": "ambulatory"}
                }
            }
        ]
    }



def make_patient():
    return {
        "resourceType": "Patient",
        "id": "17",
        "name": [{"given": ["Aisha"], "family": "Bello"}],
        "gender": "female",
        "birthDate": "1998-10-10",
    }


def test_identified_report_contains_patient_details():
    report = build_clinical_report(make_patient(), make_bundle())

    assert "Patient ID: 17" in report
    assert "Name: Aisha Bello" in report
    assert "Birth Date: 1998-10-10" in report
    assert "LOINC Code: 85354-9" in report
    assert "LOINC Code: 4548-4" in report


def test_deidentified_report_removes_direct_identifiers():
    report = build_clinical_report(
        make_patient(),
        make_bundle(),
        deidentified=True,
    )

    assert "Patient ID: [REDACTED]" in report
    assert "Name: [REDACTED]" in report
    assert "Birth Year: 1998" in report
    assert "Birth Date: 1998-10-10" not in report
    assert "DE-IDENTIFICATION NOTICE" in report
    assert "LOINC Code: 85354-9" in report
