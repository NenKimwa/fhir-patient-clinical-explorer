\# FHIR Patient Clinical Explorer



A Python command-line application for exploring patient clinical data from a local FHIR server.



This project demonstrates practical use of FHIR REST APIs, clinical data analysis, search Bundles, resource references, pagination, de-identification, clinical reporting, audit trails, and automated testing.



\## Project Overview



The FHIR Patient Clinical Explorer connects to a FHIR server and provides a simple CLI for retrieving, analyzing, and reporting patient clinical information.



The application was developed as a hands-on FHIR and healthcare data engineering project.



\## Features



\### Patient Clinical Data



\- Retrieve Patient resources by ID

\- Retrieve patient Observations

\- Retrieve related Practitioner resources

\- Retrieve related Encounter resources

\- Retrieve complete clinical search Bundles

\- Display FHIR resource types and IDs



\### FHIR Search



The project demonstrates:



\- FHIR REST API operations

\- GET, POST, PUT and DELETE requests

\- Search parameters

\- `\_include`

\- `\_include:iterate`

\- SearchSet Bundles

\- Resource references

\- FHIR pagination

\- Following server-provided `next` links

\- De-duplication of resources across pages



\### Clinical Analytics



The application provides:



\- Observation counts

\- Observations with and without values

\- Observations with and without clinical dates

\- Practitioner counts

\- Encounter counts

\- LOINC code extraction

\- Measurement values

\- Informational measurement interpretations

\- Patient insights

\- JSON export

\- CSV export



\### Clinical Reporting



The application can generate identified clinical reports containing:



\- Patient information

\- Clinical observations

\- Practitioners

\- Encounters

\- Clinical measurements



Reports can be exported as:



\- TXT

\- JSON



\### De-identified Reporting



The application also supports de-identified clinical reports.



Direct patient identifiers are removed or redacted while relevant clinical information is retained.



De-identified reports can be exported as:



\- TXT

\- JSON



\### Audit Trail



Clinical report generation and de-identified report generation are recorded in an audit log.



\## CLI Structure



```text

FHIR PATIENT CLINICAL EXPLORER



1\. View Patient Data

2\. Data Quality

3\. Clinical Reports

4\. De-identified Reports

0\. Exit



View Patient Data

1\. Patient Clinical Summary

2\. Observations

3\. Practitioner

4\. Encounter

5\. Full Clinical Bundle

0\. Back to Main Menu



Data Quality

1\. Clinical Analytics

2\. Patient Insights

3\. Export Analytics to JSON

4\. Export Analytics to CSV

0\. Back to Main Menu



Clinical Reports

1\. Generate Clinical Report

2\. Export Clinical Report to TXT

3\. Export Clinical Report to JSON

0\. Back to Main Menu



De-identified Reports

1\. Generate De-identified Report

2\. Export De-identified Report to TXT

3\. Export De-identified Report to JSON

0\. Back to Main Menu



Technology Stack

\- Python

\- FHIR R4

\- REST API

\- Requests

\- Pytest

\- JSON

\- CSV

\- Command Line Interface

Project Structure

fhir-patient-clinical-explorer/

│

├── src/

│   ├── main.py

│   ├── fhir\_client.py

│   ├── clinical\_summary.py

│   ├── clinical\_analytics.py

│   └── clinical\_report.py

│

├── tests/

│   ├── test\_clinical\_analytics.py

│   ├── test\_clinical\_report.py

│   └── test\_fhir\_client.py

│

├── .gitignore

├── README.md

└── requirements.txt



FHIR Server

The application defaults to:

http://localhost:8080/fhir



The FHIR server URL can also be configured using the FHIR\_BASE\_URL environment variable.

Example:

$env:FHIR\_BASE\_URL="http://localhost:8080/fhir"



Installation

Navigate to the project directory and install the required dependencies:

python -m pip install -r requirements.txt



Running the Application

From the project root:

python src\\main.py



The application will display the main CLI menu and allow navigation through patient data, data quality, clinical reports, and de-identified reports.

Running Tests

Run the automated test suite with:

python -m pytest -q



The project includes tests for:

\- Observation extraction

\- Clinical analytics

\- LOINC extraction

\- Observation values

\- Clinical dates

\- Measurement interpretation

\- Identified clinical reports

\- De-identified clinical reports

\- FHIR pagination

\- Resource de-duplication

Example Clinical Data

The project was tested against a local HAPI FHIR server containing example resources including:

\- Patient

\- Observation

\- Practitioner

\- Encounter

Example clinical measurements include:

\- Blood pressure

\- HbA1c

\- Heart rate support through LOINC-based measurement handling

FHIR Pagination

FHIR search results are returned as Bundles.

The client checks the Bundle pagination links and follows the server-provided:

relation = "next"



until there are no additional pages.

Resources from subsequent pages are merged while preventing duplicate resources.

Learning Outcomes

This project demonstrates practical understanding of:

\- FHIR resource structures

\- FHIR REST APIs

\- FHIR search

\- Search Bundles

\- \_include and \_include:iterate

\- Resource references

\- LOINC

\- Clinical data extraction

\- Healthcare data quality

\- Clinical analytics

\- Data de-identification

\- Clinical reporting

\- Audit logging

\- API pagination

\- Automated testing

\- Python CLI application design

Disclaimer

This project uses demonstration clinical data for educational and portfolio purposes.

Clinical interpretations displayed by the application are informational and are not intended to provide medical diagnosis or treatment recommendations.





