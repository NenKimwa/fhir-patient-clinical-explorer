import os
import requests

FHIR_BASE_URL = os.getenv(
    "FHIR_BASE_URL",
    "http://localhost:8080/fhir"
).rstrip("/")

REQUEST_TIMEOUT = 30


def get_patient(patient_id):
    """Retrieve a Patient resource by ID."""
    url = f"{FHIR_BASE_URL}/Patient/{patient_id}"

    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


def _resource_key(resource):
    """Return a stable key for de-duplicating Bundle resources."""
    resource_type = resource.get("resourceType", "")
    resource_id = resource.get("id", "")

    return f"{resource_type}/{resource_id}"


def _merge_bundle_entries(entries, new_entries):
    """Add new Bundle entries while avoiding duplicate resources."""

    existing_keys = {
        _resource_key(
            entry.get("resource", {})
        )
        for entry in entries
        if entry.get("resource")
    }

    for entry in new_entries:
        resource = entry.get("resource", {})

        if not resource:
            continue

        key = _resource_key(resource)

        if key not in existing_keys:
            entries.append(entry)
            existing_keys.add(key)


def _get_all_bundle_pages(url, params=None):
    """
    Retrieve a FHIR search Bundle and follow pagination links.

    The first request uses the supplied search parameters.
    Subsequent requests follow the server-provided `next` link
    until no next page remains.
    """

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    bundle = response.json()

    all_entries = list(
        bundle.get("entry", [])
    )

    while True:
        next_url = None

        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                next_url = link.get("url")
                break

        if not next_url:
            break

        response = requests.get(
            next_url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        bundle = response.json()

        _merge_bundle_entries(
            all_entries,
            bundle.get("entry", [])
        )

    bundle["entry"] = all_entries

    bundle["total"] = len(all_entries)

    return bundle


def get_clinical_bundle(patient_id):
    """Retrieve all Observations and related clinical resources for a patient."""

    url = f"{FHIR_BASE_URL}/Observation"

    params = [
        ("subject", f"Patient/{patient_id}"),
        ("_include", "Observation:subject"),
        ("_include", "Observation:performer"),
        ("_include:iterate", "Observation:encounter"),
    ]

    return _get_all_bundle_pages(
        url,
        params=params
    )