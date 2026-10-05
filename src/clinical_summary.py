def display_clinical_summary(patient, bundle):
    print("\n" + "=" * 50)
    print("PATIENT CLINICAL SUMMARY")
    print("=" * 50)

    # --------------------------------------------------
    # PATIENT INFORMATION
    # --------------------------------------------------

    names = patient.get("name", [])

    if names:
        name = names[0]

        given_name = " ".join(
            name.get("given", [])
        )

        family_name = name.get(
            "family",
            ""
        )

        full_name = f"{given_name} {family_name}".strip()

    else:
        full_name = "Unknown"

    print(f"Name: {full_name}")
    print(
        f"Gender: "
        f"{patient.get('gender', 'Unknown')}"
    )
    print(
        f"Birth Date: "
        f"{patient.get('birthDate', 'Unknown')}"
    )

    # --------------------------------------------------
    # CLINICAL OBSERVATIONS
    # --------------------------------------------------

    print("\n" + "-" * 50)
    print("CLINICAL OBSERVATIONS")
    print("-" * 50)

    found_observation = False

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        if resource.get(
            "resourceType"
        ) != "Observation":
            continue

        found_observation = True

        observation_id = resource.get(
            "id",
            "Unknown"
        )

        # Observation type
        coding = (
            resource
            .get("code", {})
            .get("coding", [])
        )

        if coding:
            display = coding[0].get(
                "display",
                "Unknown observation"
            )
        else:
            display = "Unknown observation"

        print(
            f"\nObservation/{observation_id}"
        )

        print(
            f"Type: {display}"
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        status = resource.get(
            "status",
            "Unknown"
        )

        print(
            f"  Status: {status}"
        )

        # --------------------------------------------------
        # CLINICAL DATE
        # --------------------------------------------------

        effective_date = resource.get(
            "effectiveDateTime"
        )

        if not effective_date:

            effective_period = resource.get(
                "effectivePeriod",
                {}
            )

            effective_date = (
                effective_period.get("start")
                or effective_period.get("end")
            )

        if not effective_date:
            effective_date = "Not available"

        print(
            f"  Clinical Date: "
            f"{effective_date}"
        )

        # --------------------------------------------------
        # LAST UPDATED
        # --------------------------------------------------

        meta = resource.get(
            "meta",
            {}
        )

        last_updated = meta.get(
            "lastUpdated",
            "Not available"
        )

        print(
            f"  Last Updated: "
            f"{last_updated}"
        )

        # --------------------------------------------------
        # OBSERVATION VALUES
        # --------------------------------------------------

        # Blood pressure / component observations
        components = resource.get(
            "component",
            []
        )

        if components:

            for component in components:

                component_coding = (
                    component
                    .get("code", {})
                    .get("coding", [])
                )

                if component_coding:
                    component_name = (
                        component_coding[0]
                        .get(
                            "display",
                            "Unknown"
                        )
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

                print(
                    f"  {component_name}: "
                    f"{value} {unit}"
                )

        # Single-value observations
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

            print(
                f"  Result: "
                f"{value} {unit}"
            )

    if not found_observation:
        print(
            "\nNo clinical observations found."
        )

    # --------------------------------------------------
    # RELATED RESOURCES
    # --------------------------------------------------

    print("\n" + "-" * 50)
    print("RELATED RESOURCES")
    print("-" * 50)

    practitioner_found = False
    encounter_found = False

    for entry in bundle.get("entry", []):

        resource = entry.get(
            "resource",
            {}
        )

        resource_type = resource.get(
            "resourceType"
        )

        # --------------------------------------------------
        # PRACTITIONER
        # --------------------------------------------------

        if resource_type == "Practitioner":

            practitioner_found = True

            practitioner_id = resource.get(
                "id",
                "Unknown"
            )

            names = resource.get(
                "name",
                []
            )

            if names:

                name = names[0]

                given = " ".join(
                    name.get("given", [])
                )

                family = name.get(
                    "family",
                    ""
                )

                practitioner_name = (
                    f"{given} {family}".strip()
                )

            else:
                practitioner_name = "Unknown"

            print(
                f"Practitioner/"
                f"{practitioner_id}: "
                f"{practitioner_name}"
            )

        # --------------------------------------------------
        # ENCOUNTER
        # --------------------------------------------------

        elif resource_type == "Encounter":

            encounter_found = True

            encounter_id = resource.get(
                "id",
                "Unknown"
            )

            encounter_status = resource.get(
                "status",
                "Unknown"
            )

            encounter_class = resource.get(
                "class",
                {}
            )

            class_display = (
                encounter_class.get(
                    "display"
                )
            )

            if not class_display:
                class_display = (
                    encounter_class.get(
                        "code",
                        "Unknown"
                    )
                )

            print(
                f"Encounter/{encounter_id}: "
                f"status={encounter_status}, "
                f"class={class_display}"
            )

    if not practitioner_found:
        print(
            "No practitioner information found."
        )

    if not encounter_found:
        print(
            "No encounter information found."
        )