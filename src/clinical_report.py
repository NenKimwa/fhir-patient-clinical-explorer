import json
from datetime import datetime


def get_patient_name(patient):
    names = patient.get("name", [])

    if not names:
        return "Unknown"

    name = names[0]

    given = " ".join(name.get("given", []))
    family = name.get("family", "")

    return f"{given} {family}".strip()


def get_birth_year(patient):
    birth_date = patient.get("birthDate")

    if not birth_date:
        return "Unknown"

    return birth_date[:4]


def get_observation_display(resource):
    coding = resource.get("code", {}).get("coding", [])

    if coding:
        return coding[0].get(
            "display",
            "Unknown observation"
        )

    return "Unknown observation"


def get_loinc_code(resource):
    coding = resource.get("code", {}).get("coding", [])

    for item in coding:
        if item.get("system") == "http://loinc.org":
            return item.get("code", "Unknown")

    return "Not available"


def get_clinical_date(resource):
    return (
        resource.get("effectiveDateTime")
        or resource.get("effectivePeriod", {}).get("start")
        or "Not available"
    )


def format_observation(resource):
    lines = []

    observation_id = resource.get("id", "Unknown")
    display = get_observation_display(resource)
    loinc_code = get_loinc_code(resource)
    clinical_date = get_clinical_date(resource)

    lines.append(f"Observation/{observation_id}")
    lines.append(f"Type: {display}")
    lines.append(f"LOINC Code: {loinc_code}")
    lines.append(f"Clinical Date: {clinical_date}")

    # Blood pressure / component-based observations
    components = resource.get("component", [])

    if components:
        for component in components:

            component_coding = (
                component
                .get("code", {})
                .get("coding", [])
            )

            if component_coding:
                component_name = component_coding[0].get(
                    "display",
                    "Unknown"
                )
            else:
                component_name = "Unknown"

            value_quantity = component.get(
                "valueQuantity",
                {}
            )

            value = value_quantity.get(
                "value",
                "Unknown"
            )

            unit = value_quantity.get(
                "unit",
                ""
            )

            lines.append(
                f"  {component_name}: {value} {unit}"
            )

    # Single-value observation
    elif "valueQuantity" in resource:

        value_quantity = resource.get(
            "valueQuantity",
            {}
        )

        value = value_quantity.get(
            "value",
            "Unknown"
        )

        unit = value_quantity.get(
            "unit",
            ""
        )

        lines.append(
            f"  Result: {value} {unit}"
        )

    return lines


def build_clinical_report(
    patient,
    bundle,
    deidentified=False
):
    """
    Build a clinical report.

    deidentified=False:
        Includes patient-identifying information.

    deidentified=True:
        Removes direct patient identifiers and
        retains only the birth year.
    """

    lines = []

    if deidentified:
        report_title = (
            "FHIR PATIENT CLINICAL REPORT "
            "(DE-IDENTIFIED)"
        )
    else:
        report_title = (
            "FHIR PATIENT CLINICAL REPORT"
        )

    lines.append("")
    lines.append("=" * 50)
    lines.append(report_title)
    lines.append("=" * 50)
    lines.append("")

    # --------------------------------------------------
    # PATIENT INFORMATION
    # --------------------------------------------------

    lines.append("PATIENT INFORMATION")
    lines.append("-" * 50)

    if deidentified:
        lines.append("Patient ID: [REDACTED]")
        lines.append("Name: [REDACTED]")
    else:
        patient_id = patient.get(
            "id",
            "Unknown"
        )

        lines.append(
            f"Patient ID: {patient_id}"
        )

        lines.append(
            f"Name: {get_patient_name(patient)}"
        )

    gender = patient.get(
        "gender",
        "Unknown"
    )

    lines.append(
        f"Gender: {gender}"
    )

    if deidentified:
        lines.append(
            f"Birth Year: {get_birth_year(patient)}"
        )
    else:
        birth_date = patient.get(
            "birthDate",
            "Unknown"
        )

        lines.append(
            f"Birth Date: {birth_date}"
        )

    lines.append("")

    # --------------------------------------------------
    # CLINICAL OBSERVATIONS
    # --------------------------------------------------

    lines.append("CLINICAL OBSERVATIONS")
    lines.append("-" * 50)

    observations = []

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        if resource.get(
            "resourceType"
        ) == "Observation":

            observations.append(resource)

    lines.append(
        f"Total Observations: {len(observations)}"
    )

    lines.append("")

    for observation in observations:

        observation_lines = format_observation(
            observation
        )

        lines.extend(
            observation_lines
        )

        lines.append("")

    # --------------------------------------------------
    # RELATED RESOURCES
    # --------------------------------------------------

    lines.append("RELATED RESOURCES")
    lines.append("-" * 50)

    practitioners = []
    encounters = []

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        resource_type = resource.get(
            "resourceType"
        )

        if resource_type == "Practitioner":
            practitioners.append(resource)

        elif resource_type == "Encounter":
            encounters.append(resource)

    lines.append(
        f"Practitioners: {len(practitioners)}"
    )

    lines.append(
        f"Encounters: {len(encounters)}"
    )

    lines.append("")

    # --------------------------------------------------
    # REPORT METADATA
    # --------------------------------------------------

    lines.append("REPORT GENERATED")
    lines.append("-" * 50)

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    lines.append(generated_at)

    lines.append("")

    if deidentified:
        lines.append(
            "DE-IDENTIFICATION NOTICE"
        )
        lines.append("-" * 50)
        lines.append(
            "Direct patient identifiers have "
            "been removed from this report."
        )
        lines.append("")

    lines.append("=" * 50)

    return "\n".join(lines)


def display_clinical_report(
    patient,
    bundle,
    deidentified=False
):
    report = build_clinical_report(
        patient,
        bundle,
        deidentified
    )

    print(report)


def export_clinical_report_txt(
    patient,
    bundle,
    filename="clinical_report.txt",
    deidentified=False
):
    report = build_clinical_report(
        patient,
        bundle,
        deidentified
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    return filename


def export_clinical_report_json(
    patient,
    bundle,
    filename="clinical_report.json",
    deidentified=False
):
    observations = []

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        if resource.get(
            "resourceType"
        ) == "Observation":

            observation_data = {
                "id": resource.get(
                    "id",
                    "Unknown"
                ),
                "type": get_observation_display(
                    resource
                ),
                "loinc_code": get_loinc_code(
                    resource
                ),
                "clinical_date": get_clinical_date(
                    resource
                )
            }

            if resource.get("component"):

                components = []

                for component in resource.get(
                    "component",
                    []
                ):

                    component_coding = (
                        component
                        .get("code", {})
                        .get("coding", [])
                    )

                    component_name = (
                        component_coding[0].get(
                            "display",
                            "Unknown"
                        )
                        if component_coding
                        else "Unknown"
                    )

                    value_quantity = (
                        component.get(
                            "valueQuantity",
                            {}
                        )
                    )

                    components.append({
                        "name": component_name,
                        "value": value_quantity.get(
                            "value"
                        ),
                        "unit": value_quantity.get(
                            "unit"
                        )
                    })

                observation_data[
                    "components"
                ] = components

            elif "valueQuantity" in resource:

                value_quantity = resource.get(
                    "valueQuantity",
                    {}
                )

                observation_data[
                    "value"
                ] = value_quantity.get(
                    "value"
                )

                observation_data[
                    "unit"
                ] = value_quantity.get(
                    "unit"
                )

            observations.append(
                observation_data
            )

    report_data = {
        "report_type": (
            "de-identified"
            if deidentified
            else "identified"
        ),
        "generated_at": datetime.now().isoformat(),
        "patient": {},
        "clinical_observations": observations,
        "related_resources": {
            "practitioners": 0,
            "encounters": 0
        }
    }

    if deidentified:

        report_data["patient"] = {
            "id": "[REDACTED]",
            "name": "[REDACTED]",
            "gender": patient.get(
                "gender",
                "Unknown"
            ),
            "birth_year": get_birth_year(
                patient
            )
        }

    else:

        report_data["patient"] = {
            "id": patient.get(
                "id",
                "Unknown"
            ),
            "name": get_patient_name(
                patient
            ),
            "gender": patient.get(
                "gender",
                "Unknown"
            ),
            "birth_date": patient.get(
                "birthDate",
                "Unknown"
            )
        }

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        resource_type = resource.get(
            "resourceType"
        )

        if resource_type == "Practitioner":

            report_data[
                "related_resources"
            ]["practitioners"] += 1

        elif resource_type == "Encounter":

            report_data[
                "related_resources"
            ]["encounters"] += 1

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report_data,
            file,
            indent=4
        )

    return filename