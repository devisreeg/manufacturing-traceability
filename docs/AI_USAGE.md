# AI Usage and Individual Contribution

## 1. Purpose

This document discloses how AI assistance was used while developing the Manufacturing Defect Traceability and CAPA System.

AI was used as a development assistant for understanding requirements, debugging, implementation guidance, test design, and documentation. The candidate remains responsible for understanding, reviewing, and validating the submitted project.

## 2. Areas Where AI Assistance Was Used

AI assistance was used during work involving:

- Python application structure and module organization.
- Synthetic manufacturing data generation.
- SQLite schema and relationships between manufacturing entities.
- Data validation and referential-integrity checks.
- Manufacturing anomaly detection rules.
- Automated test design and debugging.
- Quality metrics and dashboard development.
- Git troubleshooting and repository organization.
- Documentation and submission-readiness review.

This list describes the areas where assistance was used. It is not a claim that every line of code was written or independently verified without assistance.

## 3. Human Review and Validation

The candidate ran the project locally and reviewed the results.

Recorded verification includes:

- Synthetic dataset generation at full scale.
- Database validation checks.
- Anomaly detection on the generated dataset.
- Quality-metric calculation.
- Automated test execution using pytest.
- Git status checks to avoid committing local database files.

The latest recorded automated test run completed with 11 passing tests. The latest recorded validation run passed all seven implemented checks.

These results demonstrate the behavior observed during testing; they do not prove that every possible manufacturing scenario is handled correctly.

## 4. Important Design and Implementation Considerations

- Synthetic data is used so the project can be run without access to proprietary manufacturing data.
- SQLite keeps the application locally runnable without requiring a separate database server.
- Validation and anomaly detection are separate modules so data-integrity checks and anomaly rules can be run independently.
- Automated tests cover selected normal and invalid-data scenarios.
- The anomaly detector reports only the issue types implemented in the code.

## 5. Limitations

- The dataset is synthetic and does not establish performance on real industrial data.
- The anomaly rules are not a complete manufacturing quality-monitoring solution.
- The application does not replace expert root-cause analysis or an operational CAPA process.
- Passing tests cover only the scenarios represented by the current test suite.
- AI-assisted implementation can introduce mistakes; outputs must be reviewed and verified.

## 6. Prompt-History Record

The `docs/prompt_history/` directory is reserved for prompts used with AI tools during this project.

Only prompts that can be recovered or accurately reconstructed should be recorded as historical prompts. Reconstructed prompts must be labelled as reconstructed rather than represented as exact original wording.

The candidate should review available conversation history and other AI tools used, then add the recoverable prompts and disclose any gaps. This document alone is not a complete prompt-history archive.

## 7. Individual Ownership

The candidate is responsible for the submitted repository and should be prepared to explain the database design, generation logic, validation rules, anomaly detection, metrics, tests, dependencies, and limitations during the technical walkthrough.
