import json
import csv
from datetime import datetime


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_observation_display(resource):
    """
    Get the human-readable name of an Observation.
    """

    coding = (
        resource.get("code", {})
        .get("coding", [])
    )

    if coding:
        return coding[0].get(
            "display",
            "Unknown observation"
        )

    return "Unknown observation"


def get_loinc_code(resource):
    """
    Get the LOINC code from an Observation.
    """

    coding = (
        resource.get("code", {})
        .get("coding", [])
    )

    for item in coding:
        if item.get("system") == "http://loinc.org":
            return item.get("code", "Unknown")

    return "Unknown"


def get_clinical_date(resource):
    """
    Extract the clinical date from an Observation.

    Supports:
    - effectiveDateTime
    - effectivePeriod.start
    - effectivePeriod.end
    """

    effective_date = resource.get("effectiveDateTime")

    if effective_date:
        return effective_date

    effective_period = resource.get(
        "effectivePeriod",
        {}
    )

    return (
        effective_period.get("start")
        or effective_period.get("end")
        or None
    )


def has_observation_value(resource):
    """
    Determine whether an Observation contains
    a clinical value.
    """

    if "valueQuantity" in resource:
        return True

    for component in resource.get(
        "component",
        []
    ):
        if "valueQuantity" in component:
            return True

    return False


def get_observation_values(resource):
    """
    Extract clinical measurements from an Observation.

    Returns a list of dictionaries.
    """

    values = []

    # --------------------------------------------------------
    # Single value Observation
    # --------------------------------------------------------

    if "valueQuantity" in resource:

        quantity = resource.get(
            "valueQuantity",
            {}
        )

        values.append({
            "name": "Result",
            "value": quantity.get(
                "value",
                "Unknown"
            ),
            "unit": quantity.get(
                "unit",
                ""
            )
        })

    # --------------------------------------------------------
    # Component Observation
    # --------------------------------------------------------

    for component in resource.get(
        "component",
        []
    ):

        coding = (
            component.get("code", {})
            .get("coding", [])
        )

        if coding:
            name = coding[0].get(
                "display",
                "Unknown"
            )
        else:
            name = "Unknown"

        quantity = component.get(
            "valueQuantity",
            {}
        )

        if quantity:

            values.append({
                "name": name,
                "value": quantity.get(
                    "value",
                    "Unknown"
                ),
                "unit": quantity.get(
                    "unit",
                    ""
                )
            })

    return values


# ============================================================
# CLINICAL INTERPRETATION
# ============================================================

def interpret_measurement(
    observation_name,
    values
):
    """
    Provide simple informational interpretations
    for supported clinical measurements.

    These are analytics demonstrations,
    not medical diagnoses.
    """

    interpretations = []

    name = observation_name.lower()

    # --------------------------------------------------------
    # Blood Pressure
    # --------------------------------------------------------

    if "blood pressure" in name:

        systolic = None
        diastolic = None

        for item in values:

            item_name = item["name"].lower()

            if "systolic" in item_name:
                systolic = item["value"]

            elif "diastolic" in item_name:
                diastolic = item["value"]

        # Systolic interpretation
        if isinstance(systolic, (int, float)):

            if systolic >= 140:

                interpretations.append(
                    "Systolic blood pressure "
                    "is in a high range."
                )

            elif systolic >= 130:

                interpretations.append(
                    "Systolic blood pressure "
                    "is above the commonly "
                    "used normal range."
                )

        # Diastolic interpretation
        if isinstance(diastolic, (int, float)):

            if diastolic >= 90:

                interpretations.append(
                    "Diastolic blood pressure "
                    "is in a high range."
                )

            elif diastolic >= 80:

                interpretations.append(
                    "Diastolic blood pressure "
                    "is at the upper end of "
                    "the commonly used normal range."
                )

        # If neither value triggered an interpretation
        if not interpretations:

            interpretations.append(
                "Blood pressure values "
                "fall within the commonly "
                "used normal range."
            )

    # --------------------------------------------------------
    # HbA1c
    # --------------------------------------------------------

    elif (
        "hemoglobin a1c" in name
        or "hba1c" in name
    ):

        for item in values:

            value = item["value"]

            if isinstance(value, (int, float)):

                if value >= 6.5:

                    interpretations.append(
                        "Value is at or above "
                        "the commonly used "
                        "diabetes threshold."
                    )

                elif value >= 5.7:

                    interpretations.append(
                        "Within the commonly "
                        "used prediabetes range."
                    )

                else:

                    interpretations.append(
                        "Below the commonly "
                        "used prediabetes range."
                    )

    return interpretations


# ============================================================
# EXTRACT OBSERVATIONS
# ============================================================

def extract_observations(bundle):
    """
    Convert FHIR Observation resources into
    a simpler analytics-friendly structure.
    """

    observations = []

    for entry in bundle.get(
        "entry",
        []
    ):

        resource = entry.get(
            "resource",
            {}
        )

        if resource.get(
            "resourceType"
        ) != "Observation":

            continue

        observation = {
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
            "status": resource.get(
                "status",
                "Unknown"
            ),
            "clinical_date": get_clinical_date(
                resource
            ),
            "has_value": has_observation_value(
                resource
            ),
            "values": get_observation_values(
                resource
            )
        }

        observation["interpretations"] = (
            interpret_measurement(
                observation["type"],
                observation["values"]
            )
        )

        observations.append(
            observation
        )

    return observations


# ============================================================
# ANALYTICS SUMMARY
# ============================================================

def build_analytics(bundle):
    """
    Build the complete analytics data structure.
    """

    observations = extract_observations(
        bundle
    )

    total_observations = len(
        observations
    )

    observations_with_values = sum(
        1
        for observation in observations
        if observation["has_value"]
    )

    observations_without_values = (
        total_observations
        - observations_with_values
    )

    observations_with_dates = sum(
        1
        for observation in observations
        if observation["clinical_date"]
    )

    observations_without_dates = (
        total_observations
        - observations_with_dates
    )

    practitioners = sum(
        1
        for entry in bundle.get(
            "entry",
            []
        )
        if entry.get(
            "resource",
            {}
        ).get(
            "resourceType"
        ) == "Practitioner"
    )

    encounters = sum(
        1
        for entry in bundle.get(
            "entry",
            []
        )
        if entry.get(
            "resource",
            {}
        ).get(
            "resourceType"
        ) == "Encounter"
    )

    analytics = {
        "generated_at": datetime.now().isoformat(),

        "bundle_type": bundle.get(
            "type",
            "Unknown"
        ),

        "observation_overview": {
            "total": total_observations,

            "with_values":
                observations_with_values,

            "without_values":
                observations_without_values,

            "with_clinical_dates":
                observations_with_dates,

            "without_clinical_dates":
                observations_without_dates
        },

        "resource_overview": {
            "practitioners":
                practitioners,

            "encounters":
                encounters
        },

        "observations":
            observations
    }

    return analytics


# ============================================================
# PATIENT INSIGHTS
# ============================================================

def get_patient_resource(bundle):
    """
    Find and return the Patient resource
    from the FHIR bundle.
    """

    for entry in bundle.get(
        "entry",
        []
    ):

        resource = entry.get(
            "resource",
            {}
        )

        if resource.get(
            "resourceType"
        ) == "Patient":

            return resource

    return {}


def get_patient_name(patient):
    """
    Extract the patient's display name.
    """

    names = patient.get(
        "name",
        []
    )

    if not names:
        return "Unknown"

    name = names[0]

    given = " ".join(
        name.get(
            "given",
            []
        )
    )

    family = name.get(
        "family",
        ""
    )

    full_name = (
        f"{given} {family}"
    ).strip()

    return full_name or "Unknown"


def build_patient_insights(bundle):
    """
    Build a patient-level analytical summary
    from the FHIR bundle.

    This is an analytics summary and does not
    constitute a medical diagnosis.
    """

    analytics = build_analytics(
        bundle
    )

    patient = get_patient_resource(
        bundle
    )

    observations = analytics[
        "observations"
    ]

    overview = analytics[
        "observation_overview"
    ]

    resources = analytics[
        "resource_overview"
    ]

    insights = {
        "generated_at":
            analytics["generated_at"],

        "patient": {
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
        },

        "key_measurements": [],

        "resource_overview": {
            "observations":
                overview["total"],
            "practitioners":
                resources["practitioners"],
            "encounters":
                resources["encounters"]
        },

        "data_quality": {
            "observations_with_values":
                overview["with_values"],
            "observations_without_values":
                overview["without_values"],
            "observations_with_clinical_dates":
                overview["with_clinical_dates"],
            "observations_without_clinical_dates":
                overview["without_clinical_dates"]
        }
    }

    # --------------------------------------------------------
    # Add measurements
    # --------------------------------------------------------

    for observation in observations:

        measurement = {
            "observation_id":
                observation["id"],

            "type":
                observation["type"],

            "loinc_code":
                observation["loinc_code"],

            "clinical_date":
                observation["clinical_date"]
                or "Not available",

            "values":
                observation["values"],

            "interpretations":
                observation["interpretations"]
        }

        insights[
            "key_measurements"
        ].append(
            measurement
        )

    return insights


def display_patient_insights(bundle):
    """
    Display a patient-level analytical
    summary in the terminal.
    """

    insights = build_patient_insights(
        bundle
    )

    patient = insights[
        "patient"
    ]

    measurements = insights[
        "key_measurements"
    ]

    resources = insights[
        "resource_overview"
    ]

    quality = insights[
        "data_quality"
    ]

    print(
        "\n" + "=" * 50
    )

    print(
        "PATIENT INSIGHTS"
    )

    print(
        "=" * 50
    )

    # --------------------------------------------------------
    # Patient
    # --------------------------------------------------------

    print(
        "\nPATIENT"
    )

    print(
        "-" * 50
    )

    print(
        f"Name: {patient['name']}"
    )

    print(
        f"Patient ID: {patient['id']}"
    )

    print(
        f"Gender: {patient['gender']}"
    )

    print(
        f"Birth Date: {patient['birth_date']}"
    )

    # --------------------------------------------------------
    # Key measurements
    # --------------------------------------------------------

    print(
        "\nKEY CLINICAL MEASUREMENTS"
    )

    print(
        "-" * 50
    )

    if not measurements:

        print(
            "No clinical measurements found."
        )

    else:

        for measurement in measurements:

            print(
                f"\nObservation/"
                f"{measurement['observation_id']}"
            )

            print(
                f"Type: "
                f"{measurement['type']}"
            )

            print(
                f"LOINC Code: "
                f"{measurement['loinc_code']}"
            )

            print(
                f"Clinical Date: "
                f"{measurement['clinical_date']}"
            )

            for value in measurement[
                "values"
            ]:

                print(
                    f"  {value['name']}: "
                    f"{value['value']} "
                    f"{value['unit']}"
                )

            for interpretation in measurement[
                "interpretations"
            ]:

                print(
                    f"  Interpretation: "
                    f"{interpretation}"
                )

    # --------------------------------------------------------
    # Resource overview
    # --------------------------------------------------------

    print(
        "\nFHIR DATA OVERVIEW"
    )

    print(
        "-" * 50
    )

    print(
        f"Observations: "
        f"{resources['observations']}"
    )

    print(
        f"Practitioners: "
        f"{resources['practitioners']}"
    )

    print(
        f"Encounters: "
        f"{resources['encounters']}"
    )

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    print(
        "\nDATA QUALITY"
    )

    print(
        "-" * 50
    )

    print(
        f"Observations with clinical dates: "
        f"{quality['observations_with_clinical_dates']}"
    )

    print(
        f"Observations without clinical dates: "
        f"{quality['observations_without_clinical_dates']}"
    )

    print(
        f"Observations with values: "
        f"{quality['observations_with_values']}"
    )

    print(
        f"Observations without values: "
        f"{quality['observations_without_values']}"
    )

    if quality[
        "observations_without_clinical_dates"
    ] > 0:

        print(
            "\nWarning: Some observations "
            "do not contain a clinical date."
        )

    if quality[
        "observations_without_values"
    ] > 0:

        print(
            "Warning: Some observations "
            "do not contain clinical values."
        )

    print(
        "\n" + "-" * 50
    )

    print(
        "END OF PATIENT INSIGHTS"
    )

    print(
        "-" * 50
    )


# ============================================================
# DISPLAY ANALYTICS
# ============================================================

def display_clinical_analytics(bundle):

    analytics = build_analytics(
        bundle
    )

    overview = analytics[
        "observation_overview"
    ]

    resources = analytics[
        "resource_overview"
    ]

    print(
        "\n" + "=" * 50
    )

    print(
        "CLINICAL ANALYTICS"
    )

    print(
        "=" * 50
    )

    # --------------------------------------------------------
    # Observation overview
    # --------------------------------------------------------

    print(
        "\nOBSERVATION OVERVIEW"
    )

    print(
        "-" * 50
    )

    print(
        f"Total Observations: "
        f"{overview['total']}"
    )

    print(
        f"Observations with values: "
        f"{overview['with_values']}"
    )

    print(
        f"Observations without values: "
        f"{overview['without_values']}"
    )

    print(
        f"Observations with clinical dates: "
        f"{overview['with_clinical_dates']}"
    )

    print(
        f"Observations without clinical dates: "
        f"{overview['without_clinical_dates']}"
    )

    # --------------------------------------------------------
    # Resource overview
    # --------------------------------------------------------

    print(
        "\nRESOURCE OVERVIEW"
    )

    print(
        "-" * 50
    )

    print(
        f"Practitioners: "
        f"{resources['practitioners']}"
    )

    print(
        f"Encounters: "
        f"{resources['encounters']}"
    )

    # --------------------------------------------------------
    # Clinical measurements
    # --------------------------------------------------------

    print(
        "\nCLINICAL MEASUREMENTS"
    )

    print(
        "-" * 50
    )

    for observation in analytics[
        "observations"
    ]:

        print(
            f"\nObservation/"
            f"{observation['id']}"
        )

        print(
            f"Type: "
            f"{observation['type']}"
        )

        print(
            f"LOINC Code: "
            f"{observation['loinc_code']}"
        )

        clinical_date = (
            observation["clinical_date"]
            or "Not available"
        )

        print(
            f"Clinical Date: "
            f"{clinical_date}"
        )

        for value in observation[
            "values"
        ]:

            print(
                f"  {value['name']}: "
                f"{value['value']} "
                f"{value['unit']}"
            )

        for interpretation in observation[
            "interpretations"
        ]:

            print(
                f"  Interpretation: "
                f"{interpretation}"
            )

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    print(
        "\n" + "-" * 50
    )

    print(
        "CLINICAL DATA QUALITY"
    )

    print(
        "-" * 50
    )

    print(
        f"Missing clinical dates: "
        f"{overview['without_clinical_dates']}"
    )

    print(
        f"Observations missing values: "
        f"{overview['without_values']}"
    )

    if overview[
        "without_clinical_dates"
    ] > 0:

        print(
            "Warning: Some observations "
            "do not contain a clinical date."
        )

    else:

        print(
            "All observations contain "
            "clinical dates."
        )

    print(
        "\n" + "-" * 50
    )

    print(
        "END OF CLINICAL ANALYTICS"
    )

    print(
        "-" * 50
    )


# ============================================================
# EXPORT JSON
# ============================================================

def export_analytics_json(
    bundle,
    filename="clinical_analytics.json"
):

    analytics = build_analytics(
        bundle
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            analytics,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nAnalytics successfully exported to:"
        f"\n{filename}"
    )


# ============================================================
# EXPORT CSV
# ============================================================

def export_analytics_csv(
    bundle,
    filename="clinical_analytics.csv"
):

    analytics = build_analytics(
        bundle
    )

    rows = []

    for observation in analytics[
        "observations"
    ]:

        if observation["values"]:

            for value in observation[
                "values"
            ]:

                rows.append({

                    "Observation ID":
                        observation["id"],

                    "Type":
                        observation["type"],

                    "LOINC Code":
                        observation["loinc_code"],

                    "Status":
                        observation["status"],

                    "Clinical Date":
                        observation["clinical_date"]
                        or "Not available",

                    "Measurement":
                        value["name"],

                    "Value":
                        value["value"],

                    "Unit":
                        value["unit"]
                })

        else:

            rows.append({

                "Observation ID":
                    observation["id"],

                "Type":
                    observation["type"],

                "LOINC Code":
                    observation["loinc_code"],

                "Status":
                    observation["status"],

                "Clinical Date":
                    observation["clinical_date"]
                    or "Not available",

                "Measurement":
                    "",

                "Value":
                    "",

                "Unit":
                    ""
            })

    fieldnames = [
        "Observation ID",
        "Type",
        "LOINC Code",
        "Status",
        "Clinical Date",
        "Measurement",
        "Value",
        "Unit"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    print(
        f"\nAnalytics successfully exported to:"
        f"\n{filename}"
    )