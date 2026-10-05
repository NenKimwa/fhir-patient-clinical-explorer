import requests
from datetime import datetime

from fhir_client import get_patient, get_clinical_bundle
from clinical_summary import display_clinical_summary
from clinical_analytics import (
    display_clinical_analytics,
    display_patient_insights,
    export_analytics_json,
    export_analytics_csv,
)
from clinical_report import (
    display_clinical_report,
    export_clinical_report_txt,
    export_clinical_report_json,
)


def print_header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def print_section(title):
    print("\n" + "-" * 50)
    print(title)
    print("-" * 50)


def display_observations(bundle):
    print_section("OBSERVATIONS")
    found = False

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Observation":
            continue

        found = True
        observation_id = resource.get("id", "Unknown")
        coding = resource.get("code", {}).get("coding", [])
        display = coding[0].get("display", "Unknown observation") if coding else "Unknown observation"
        print(f"\nObservation/{observation_id}")
        print(f"Type: {display}")
        print(f"Status: {resource.get('status', 'Unknown')}")

        components = resource.get("component", [])
        if components:
            for component in components:
                coding = component.get("code", {}).get("coding", [])
                name = coding[0].get("display", "Unknown") if coding else "Unknown"
                quantity = component.get("valueQuantity", {})
                print(f"  {name}: {quantity.get('value', 'Unknown')} {quantity.get('unit', '')}")
        elif "valueQuantity" in resource:
            quantity = resource.get("valueQuantity", {})
            print(f"  Result: {quantity.get('value', 'Unknown')} {quantity.get('unit', '')}")

    if not found:
        print("\nNo observations found.")


def display_practitioners(bundle):
    print_section("PRACTITIONERS")
    found = False

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Practitioner":
            continue
        found = True
        practitioner_id = resource.get("id", "Unknown")
        names = resource.get("name", [])
        if names:
            name = names[0]
            full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}".strip()
        else:
            full_name = "Unknown"
        print(f"Practitioner/{practitioner_id}: {full_name}")

    if not found:
        print("\nNo practitioner information found.")


def display_encounters(bundle):
    print_section("ENCOUNTERS")
    found = False

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Encounter":
            continue
        found = True
        encounter_id = resource.get("id", "Unknown")
        encounter_class = resource.get("class", {})
        class_display = encounter_class.get("display") or encounter_class.get("code", "Unknown")
        print(f"Encounter/{encounter_id}")
        print(f"  Status: {resource.get('status', 'Unknown')}")
        print(f"  Class: {class_display}")

    if not found:
        print("\nNo encounter information found.")


def display_full_bundle(bundle):
    print_section("FHIR BUNDLE")
    print(f"Bundle Type: {bundle.get('type', 'Unknown')}")
    print(f"Total Resources: {len(bundle.get('entry', []))}")

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType", "Unknown")
        resource_id = resource.get("id", "Unknown")
        search_mode = entry.get("search", {}).get("mode", "Unknown")
        print(f"{resource_type}/{resource_id} | search.mode: {search_mode}")


def write_audit_log(action, patient_id, filename):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audit_filename = "clinical_report_audit.log"
    with open(audit_filename, "a", encoding="utf-8") as file:
        file.write(
            f"{timestamp} | Action: {action} | "
            f"Patient ID: {patient_id} | File: {filename}\n"
        )
    return audit_filename


def patient_data_menu(patient, bundle):
    while True:
        print_header("VIEW PATIENT DATA")
        print("1. Patient Clinical Summary")
        print("2. Observations")
        print("3. Practitioner")
        print("4. Encounter")
        print("5. Full Clinical Bundle")
        print("0. Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_clinical_summary(patient, bundle)
        elif choice == "2":
            display_observations(bundle)
        elif choice == "3":
            display_practitioners(bundle)
        elif choice == "4":
            display_encounters(bundle)
        elif choice == "5":
            display_full_bundle(bundle)
        elif choice == "0":
            break
        else:
            print("\nInvalid option. Please select 0-5.")


def data_quality_menu(bundle):
    while True:
        print_header("DATA QUALITY")
        print("1. Clinical Analytics")
        print("2. Patient Insights")
        print("3. Export Analytics to JSON")
        print("4. Export Analytics to CSV")
        print("0. Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_clinical_analytics(bundle)
        elif choice == "2":
            display_patient_insights(bundle)
        elif choice == "3":
            filename = export_analytics_json(bundle)
            
        elif choice == "4":
            filename = export_analytics_csv(bundle)
            
        elif choice == "0":
            break
        else:
            print("\nInvalid option. Please select 0-4.")


def clinical_reports_menu(patient, bundle, patient_id):
    while True:
        print_header("CLINICAL REPORTS")
        print("1. Generate Clinical Report")
        print("2. Export Clinical Report to TXT")
        print("3. Export Clinical Report to JSON")
        print("0. Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_clinical_report(patient, bundle)
        elif choice == "2":
            filename = export_clinical_report_txt(patient, bundle)
            print(f"\nClinical report TXT exported to: {filename}")
            audit_file = write_audit_log("Export identified clinical report TXT", patient_id, filename)
            print(f"Audit trail updated: {audit_file}")
        elif choice == "3":
            filename = export_clinical_report_json(patient, bundle)
            print(f"\nClinical report JSON exported to: {filename}")
            audit_file = write_audit_log("Export identified clinical report JSON", patient_id, filename)
            print(f"Audit trail updated: {audit_file}")
        elif choice == "0":
            break
        else:
            print("\nInvalid option. Please select 0-3.")


def deidentified_reports_menu(patient, bundle, patient_id):
    while True:
        print_header("DE-IDENTIFIED REPORTS")
        print("1. Generate De-identified Report")
        print("2. Export De-identified Report to TXT")
        print("3. Export De-identified Report to JSON")
        print("0. Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_clinical_report(patient, bundle, deidentified=True)
        elif choice == "2":
            filename = export_clinical_report_txt(
                patient, bundle,
                filename="clinical_report_deidentified.txt",
                deidentified=True
            )
            print(f"\nDe-identified report TXT exported to: {filename}")
            audit_file = write_audit_log("Export de-identified clinical report TXT", patient_id, filename)
            print(f"Audit trail updated: {audit_file}")
        elif choice == "3":
            filename = export_clinical_report_json(
                patient, bundle,
                filename="clinical_report_deidentified.json",
                deidentified=True
            )
            print(f"\nDe-identified report JSON exported to: {filename}")
            audit_file = write_audit_log("Export de-identified clinical report JSON", patient_id, filename)
            print(f"Audit trail updated: {audit_file}")
        elif choice == "0":
            break
        else:
            print("\nInvalid option. Please select 0-3.")


def display_main_menu():
    print_header("FHIR PATIENT CLINICAL EXPLORER")
    print("\nWhat would you like to do?")
    print("1. View Patient Data")
    print("2. Data Quality")
    print("3. Clinical Reports")
    print("4. De-identified Reports")
    print("0. Exit")


def main():
    print_header("FHIR PATIENT CLINICAL EXPLORER")
    patient_id = input("Enter Patient ID: ").strip()

    if not patient_id:
        print("\nPatient ID cannot be empty.")
        return

    try:
        print("\nConnecting to FHIR server...")
        patient = get_patient(patient_id)
        bundle = get_clinical_bundle(patient_id)
        print(f"Patient {patient_id} loaded successfully.")

        while True:
            display_main_menu()
            choice = input("\nSelect an option: ").strip()

            if choice == "1":
                patient_data_menu(patient, bundle)
            elif choice == "2":
                data_quality_menu(bundle)
            elif choice == "3":
                clinical_reports_menu(patient, bundle, patient_id)
            elif choice == "4":
                deidentified_reports_menu(patient, bundle, patient_id)
            elif choice == "0":
                print("\nExiting FHIR Patient Clinical Explorer.")
                break
            else:
                print("\nInvalid option. Please select 0-4.")

    except requests.exceptions.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            print(f"\nError: Patient {patient_id} was not found.")
        else:
            print(f"\nFHIR server error: {error}")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the FHIR server.")
    except requests.exceptions.Timeout:
        print("\nError: The FHIR server request timed out.")
    except requests.exceptions.RequestException as error:
        print(f"\nRequest error: {error}")


if __name__ == "__main__":
    main()
