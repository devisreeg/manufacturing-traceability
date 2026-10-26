# Manufacturing Defect Traceability & CAPA System

An end-to-end manufacturing defect traceability and Corrective and Preventive Action (CAPA) system built with Python, SQLite, and Streamlit. The project uses synthetic manufacturing data to demonstrate production traceability, data validation, quality metrics, and anomaly detection.

## Project Overview

Manufacturing quality teams need to identify defects, trace them to their production orders and material suppliers, and track corrective actions.

This project provides a structured system for exploring manufacturing quality data, validating relationships between records, detecting selected data anomalies, and monitoring quality metrics through a dashboard.

## Features

- **Synthetic Data Generation:** Generate sample manufacturing data for products, suppliers, material lots, production orders, inspections, defects, and corrective actions.
- **Manufacturing Traceability:** Link defect records to inspection results, production orders, products, material lots, suppliers, process steps, and machines.
- **Data Validation:** Run validation checks for referential integrity, inspection quantities, material consumption, and CAPA records.
- **Anomaly Detection:** Identify selected data-quality issues, including invalid defect quantities, invalid closed CAPAs, and excessive material consumption.
- **Quality Metrics:** Calculate manufacturing and defect-related metrics.
- **Interactive Dashboard:** Explore project metrics through a Streamlit dashboard.
- **Automated Tests:** Use pytest to test data generation, validation, and anomaly detection.

## Technology Stack

- **Language:** Python
- **Database:** SQLite
- **Dashboard:** Streamlit
- **Data Processing:** Pandas
- **Testing:** Pytest
- **Version Control:** Git and GitHub

## Project Structure

```text
manufacturing-traceability/
├── app/
│   ├── __init__.py
│   ├── anomaly_detection.py
│   ├── dashboard.py
│   ├── database.py
│   ├── generator.py
│   ├── metrics.py
│   ├── traceability.py
│   └── validation.py
├── data/
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

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/devisreeg/manufacturing-traceability.git
cd manufacturing-traceability
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python 3.11 is unavailable, use another Python version compatible with the dependencies.

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Generate Synthetic Data

Generate the small sample dataset:

```bash
python -m app.generator
```

The generator also supports a full-scale option:

```bash
python -m app.generator --scale full
```

Use the small dataset first to verify that the application works in your environment.

## Run Data Validation

```bash
python -m app.validation
```

This runs the implemented data-integrity checks and reports their results.

## Run Anomaly Detection

```bash
python -m app.anomaly_detection
```

This checks for the supported manufacturing data anomalies implemented in the project.

## View Traceability Results

```bash
python -m app.traceability
```

This runs the traceability module to retrieve linked defect and production information.

## Calculate Quality Metrics

```bash
python -m app.metrics
```

This calculates the metrics implemented by the project.

## Launch the Dashboard

```bash
python -m streamlit run app/dashboard.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to explore the dashboard.

## Run Automated Tests

```bash
python -m pytest -v
```

The tests cover synthetic data generation, validation, and anomaly detection.

## Database Design

The database schema is defined in `schemas/schema.sql`. The project models manufacturing entities such as:

- Products and suppliers
- Bills of materials and material lots
- Machines and process steps
- Production orders and material consumption
- Inspection plans and inspection results
- Defects and corrective actions
- Event history

Refer to `schemas/data_dictionary.md` for the documented data definitions.

## Important Notes

- The project uses synthetic data for demonstration and testing.
- Anomaly detection covers the specific checks implemented in the code; it is not a complete industrial quality-monitoring solution.
- Metrics and validation results depend on the generated dataset and the current implementation.

## Future Improvements

- Add richer root-cause analysis and CAPA workflow reporting.
- Expand validation rules and anomaly detection.
- Add filtering and drill-down capabilities to the dashboard.
- Add support for larger datasets and more comprehensive integration tests.

## Author

**Devisree G**

GitHub: [@devisreeg](https://github.com/devisreeg)

## Export Data

Export the full dataset with `python -m app.exports --scale full`. The export includes CSV files for 13 tables, a JSON export, an SQL dump, and a manifest containing record counts and SHA-256 checksums.

The current full dataset contains 50,662 records across 13 tables.

## Ground Truth and AI Usage

See `data/ground_truth.csv` for expected anomaly decisions, `docs/AI_USAGE.md` for AI usage disclosures, and `docs/prompt_history/README.md` for prompt-history notes. This is a demonstration system using synthetic data.
