import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import fhir_client


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_get_clinical_bundle_follows_next_page(monkeypatch):
    first_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 4,
        "entry": [
            {"resource": {
                "resourceType": "Observation",
                "id": "18"
            }},
            {"resource": {
                "resourceType": "Patient",
                "id": "17"
            }},
        ],
        "link": [
            {
                "relation": "next",
                "url": "http://localhost:8080/fhir/Observation?page=2"
            }
        ],
    }

    second_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {"resource": {
                "resourceType": "Observation",
                "id": "52"
            }},
            {"resource": {
                "resourceType": "Practitioner",
                "id": "19"
            }},
            {"resource": {
                "resourceType": "Encounter",
                "id": "53"
            }},
        ],
        "link": [],
    }

    responses = [
        FakeResponse(first_page),
        FakeResponse(second_page),
    ]

    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return responses.pop(0)

    monkeypatch.setattr(fhir_client.requests, "get", fake_get)

    bundle = fhir_client.get_clinical_bundle("17")

    resource_keys = {
        f'{entry["resource"]["resourceType"]}/{entry["resource"]["id"]}'
        for entry in bundle["entry"]
    }

    assert resource_keys == {
        "Observation/18",
        "Observation/52",
        "Patient/17",
        "Practitioner/19",
        "Encounter/53",
    }

    assert bundle["total"] == 5
    assert len(calls) == 2

    assert calls[0][0].endswith("/Observation")
    assert calls[0][1]["params"][0] == ("subject", "Patient/17")

    assert calls[1][0] == (
        "http://localhost:8080/fhir/Observation?page=2"
    )
    assert "params" not in calls[1][1]


def test_pagination_deduplicates_resources(monkeypatch):
    first_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {"resource": {
                "resourceType": "Observation",
                "id": "18"
            }}
        ],
        "link": [
            {
                "relation": "next",
                "url": "http://example.test/page-2"
            }
        ],
    }

    second_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {"resource": {
                "resourceType": "Observation",
                "id": "18"
            }},
            {"resource": {
                "resourceType": "Observation",
                "id": "52"
            }},
        ],
        "link": [],
    }

    responses = [
        FakeResponse(first_page),
        FakeResponse(second_page),
    ]

    def fake_get(url, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(fhir_client.requests, "get", fake_get)

    bundle = fhir_client.get_clinical_bundle("17")

    ids = [
        entry["resource"]["id"]
        for entry in bundle["entry"]
    ]

    assert ids == ["18", "52"]
    assert bundle["total"] == 2
