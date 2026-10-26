# Manufacturing Defect Traceability & CAPA System

A Python-based manufacturing quality and traceability system built with **SQLite, Streamlit, and Pandas**. It generates synthetic manufacturing data, traces defects through production and material records, validates data integrity, detects selected anomalies, and tracks Corrective and Preventive Actions (CAPA).

The project demonstrates how structured manufacturing data can support quality monitoring, defect investigation, and traceability analysis.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Generate Synthetic Data](#generate-synthetic-data)
- [Data Validation](#data-validation)
- [Anomaly Detection](#anomaly-detection)
- [Traceability Analysis](#traceability-analysis)
- [Quality Metrics](#quality-metrics)
- [Interactive Dashboard](#interactive-dashboard)
- [Automated Tests](#automated-tests)
- [Data Export](#data-export)
- [Database Design](#database-design)
- [Ground Truth and Testing Scope](#ground-truth-and-testing-scope)
- [AI Usage and Transparency](#ai-usage-and-transparency)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Author](#author)

## Project Overview

Manufacturing quality teams need reliable ways to investigate defects, identify affected production orders, trace material usage, and monitor corrective actions.

This project implements a demonstration workflow that connects manufacturing records across multiple related database tables.

The system supports:

1. Generating reproducible synthetic manufacturing data.
2. Linking defects to inspections, production orders, products, material lots, suppliers, process steps, and machines.
3. Checking database integrity and manufacturing data constraints.
4. Detecting selected data-quality and traceability anomalies.
5. Calculating production and quality metrics.
6. Exploring manufacturing information through a Streamlit dashboard.
7. Exporting database tables into CSV, JSON, and SQL formats.

The application uses a local SQLite database and synthetic data. It is intended for demonstration, experimentation, and technical evaluation rather than direct use in a production manufacturing environment.

## Key Features

### 1. Synthetic Data Generation

Generate reproducible sample data representing manufacturing operations, including products, suppliers, material lots, production orders, inspections, defects, and corrective actions.

The generator supports small and full dataset configurations.

### 2. Manufacturing Traceability

Connect defect records to relevant manufacturing entities, including:

- Inspection results
- Production orders
- Products
- Material lots and suppliers
- Material consumption
- Process steps and machines
- Corrective actions

These relationships support investigation of the production context associated with recorded defects.

### 3. Data Validation

Run validation checks for data integrity and manufacturing constraints, including:

- Foreign-key integrity
- Defects linked to inspection records
- Defects linked to production orders
- Inspection and defect quantity consistency
- Material consumption constraints
- Corrective actions associated with defects
- Verification requirements for closed corrective actions

The validation module reports the checks implemented in the current codebase.

### 4. Anomaly Detection

Detect selected manufacturing data-quality issues, including:

- Defect quantities exceeding inspected quantities
- Material consumption exceeding available quantities
- Required bill-of-materials materials missing from production consumption
- Defects referencing nonexistent material lots
- Broken traceability relationships
- Corrective actions closed before successful verification

Detection coverage is limited to the rules implemented in the application.

### 5. Quality Metrics

Calculate production and quality metrics from the generated dataset, including production volumes, inspection quantities, defect statistics, and corrective-action status.

Metric values depend on the dataset and the implemented calculations.

### 6. Interactive Dashboard

Use the Streamlit dashboard to explore available manufacturing and quality information.

### 7. Automated Testing

Use pytest to test selected generator, validation, and anomaly-detection scenarios.

### 8. Data Export and Integrity Checks

Export database tables as CSV files, a consolidated JSON file, and an SQL dump. A manifest records export metadata, table record counts, file sizes, and SHA-256 checksums for the generated data files.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Database | SQLite |
| Dashboard | Streamlit |
| Data processing | Pandas |
| Automated testing | pytest |
| Version control | Git and GitHub |
| Export formats | CSV, JSON, SQL |
| Integrity verification | SQLite integrity check and SHA-256 checksums |

## Project Structure

```text
manufacturing-traceability/
├── app/
│   ├── __init__.py
│   ├── anomaly_detection.py
│   ├── dashboard.py
│   ├── database.py
│   ├── exports.py
│   ├── generator.py
│   ├── metrics.py
│   ├── traceability.py
│   └── validation.py
├── data/
│   └── ground_truth.csv
├── docs/
│   ├── AI_USAGE.md
│   └── prompt_history/
│       └── README.md
├── exports/
│   ├── csv/
│   ├── manifest.json
│   ├── manufacturing_export.json
│   └── manufacturing_export.sql
├── schemas/
│   ├── data_dictionary.md
│   └── schema.sql
├── tests/
│   ├── test_anomaly_detection.py
│   ├── test_generator.py
│   └── test_validation.py
├── .gitignore
├── README.md
└── requirements.txt
```

The local SQLite database and Python virtual environment are excluded from version control. Export files are provided separately from the local database.

## Getting Started

### Prerequisites

- Python 3.11 recommended
- Git
- A terminal such as Windows PowerShell
- Internet access to clone the repository and install dependencies

### 1. Clone the Repository

```powershell
git clone https://github.com/devisreeg/manufacturing-traceability.git
cd manufacturing-traceability
```

### 2. Create and Activate a Virtual Environment

On Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python 3.11 is unavailable, use a compatible Python version and verify dependency compatibility.

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Generate Synthetic Data

### Generate a Small Dataset

Start with the small dataset to verify that the application works in your environment.

```powershell
python -m app.generator
```

### Generate the Full Dataset

To generate the full dataset:

```powershell
python -m app.generator --scale full
```

The full dataset configuration uses seed `20261022` to support reproducible generation.

The verified full dataset contains **50,662 records across 13 database tables**.

Generating data initializes the local database and replaces its generated contents. Back up any local data you want to preserve before regenerating it.

## Data Validation

Run the implemented database and manufacturing data-integrity checks:

```powershell
python -m app.validation
```

Review the output for passed checks and reported issues.

For the verified full dataset, all seven implemented validation checks passed with zero reported issues.

## Anomaly Detection

Run the implemented anomaly-detection rules:

```powershell
python -m app.anomaly_detection
```

The clean generated dataset previously produced no detected anomalies. Tests also cover selected deliberately invalid or inconsistent scenarios.

A clean result means no issues were detected by the implemented rules; it does not establish that every possible manufacturing anomaly has been ruled out.

## Traceability Analysis

Run the traceability module:

```powershell
python -m app.traceability
```

This executes the traceability functionality implemented in the project to retrieve related defect and production information.

## Quality Metrics

Calculate the available manufacturing and quality metrics:

```powershell
python -m app.metrics
```

The reported results depend on the generated dataset and the current metric definitions.

## Interactive Dashboard

Launch the Streamlit dashboard:

```powershell
python -m streamlit run app/dashboard.py
```

Streamlit displays a local URL in the terminal. Open that URL in your browser to interact with the dashboard.

Keep the terminal running while using the application.

## Automated Tests

Run the test suite:

```powershell
python -m pytest -v
```

The verified test suite contains **11 tests**, covering selected scenarios for:

- Synthetic data generation
- Anomaly detection
- Foreign-key integrity
- Corrective-action relationships
- Inspection quantity validation

**Latest recorded test result:** 11 passed.

The generator test uses a temporary database so it does not overwrite the main project database during that test.

Test coverage is limited to the scenarios currently implemented in the test suite.

## Data Export

The repository includes CSV, JSON, and SQL exports generated from the full dataset.

To regenerate the exports from the local database:

```powershell
python -m app.exports --scale full
```

The export process checks SQLite database integrity before writing the output files.

Generated artifacts:

| Artifact | Description |
|---|---|
| `exports/csv/` | Individual CSV files for the 13 database tables |
| `exports/manufacturing_export.json` | Consolidated JSON export containing table data and metadata |
| `exports/manufacturing_export.sql` | SQL dump generated from the database |
| `exports/manifest.json` | Export metadata, table record counts, file sizes, and SHA-256 checksums |

### Recommended Full Export Workflow

Generate the full dataset, validate it, run anomaly detection, and then export it:

```powershell
python -m app.generator --scale full
python -m app.validation
python -m app.anomaly_detection
python -m app.exports --scale full
```

**Important:** The export command's `--scale` argument labels the export metadata. It does not generate the requested dataset or independently verify that the existing database contains the full dataset. Generate the intended dataset before exporting.

The manifest contains checksums for the generated CSV, JSON, and SQL files. These can be used to detect changes to the exported files.

## Database Design

The database schema is defined in `schemas/schema.sql`. It models the relationships among manufacturing and quality entities.

The database contains 13 tables:

1. `products`
2. `suppliers`
3. `bom`
4. `material_lots`
5. `machines`
6. `production_orders`
7. `order_material_consumption`
8. `process_steps`
9. `inspection_plans`
10. `inspection_results`
11. `defects`
12. `corrective_actions`
13. `event_history`

The schema uses relational constraints and indexes to support data integrity and record relationships.

Refer to `schemas/data_dictionary.md` for documented table and field definitions.

## Ground Truth and Testing Scope

The file `data/ground_truth.csv` contains five documented anomaly or traceability scenarios with expected decisions:

| Case | Scenario | Expected decision |
|---|---|---|
| GT-001 | Defect references a nonexistent material lot | REJECT |
| GT-002 | Required BOM material is missing from production consumption | FLAG |
| GT-003 | Corrective action is closed before successful verification | REJECT |
| GT-004 | Defect quantity exceeds inspected quantity | REJECT |
| GT-005 | Required traceability chain is broken | FLAG |

These scenarios document expected outcomes for selected cases. They should not be interpreted as proof that every scenario is automatically evaluated by a separate ground-truth benchmarking framework.

## AI Usage and Transparency

AI assistance was used during project development. The scope of that assistance, review responsibilities, and known limitations are documented in:

- `docs/AI_USAGE.md`
- `docs/prompt_history/README.md`

The prompt-history documentation identifies reconstructed prompts where exact original wording was not preserved.

The project implementation and test results were reviewed during development. The author remains responsible for understanding, explaining, and defending the implementation.

## Limitations

- The dataset is synthetic and does not represent actual factory operations.
- Anomaly detection covers selected rules rather than every possible quality issue.
- Traceability and validation depend on the relationships and constraints implemented in the database.
- The automated test suite covers selected scenarios and is not exhaustive.
- The application has not been established as a production-ready industrial quality-management system.
- Reported metrics depend on the generated data and implemented calculations.
- Export metadata describes the export operation and does not independently establish the correctness of every record.

## Future Improvements

Potential improvements include:

- More comprehensive root-cause analysis
- Expanded anomaly-detection and validation rules
- More extensive integration and edge-case testing
- Additional dashboard filtering and drill-down features
- Improved CAPA workflow reporting
- More automated ground-truth evaluation
- Additional export and restore verification
- Support for integration with external manufacturing systems

## Author

**Devisree G**

GitHub: [@devisreeg](https://github.com/devisreeg)

Repository: [manufacturing-traceability](https://github.com/devisreeg/manufacturing-traceability)