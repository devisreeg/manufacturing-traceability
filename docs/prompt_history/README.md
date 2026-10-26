# AI Prompt History

## Important disclosure

This folder records AI prompts used during development of the Manufacturing Defect Traceability and CAPA System.

The project brief below is reconstructed from available conversation context. It is NOT a verbatim copy of the original prompt.

The candidate must review available ChatGPT conversation history and any other AI tools used to recover additional prompts. Do not represent reconstructed wording as an exact historical prompt.

## Record 001 — Original Project Brief (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary
**Date:** 2026-10-26
**Status:** Original wording not fully available

### Reconstructed brief

Build an end-to-end manufacturing defect traceability and CAPA system that can trace defects through inspection results, production orders, material lots, suppliers, machines, and corrective actions.

The project brief included the following requirements:

- Generate deterministic synthetic manufacturing data using seed `20261022`.
- Generate 200 SKUs/products, 50 suppliers, 2,000 material lots, 5,000 production orders, and 20,000 inspections.
- Include five labelled anomaly or edge-case scenarios and maintain a separate ground-truth file.
- Implement data validation and manufacturing traceability.
- Calculate useful manufacturing quality metrics.
- Provide a dashboard or other suitable way to explore results.
- Include CSV, JSON, and SQL exports.
- Support reproducibility and document how results can be verified.
- Include a README, automated tests, and a public GitHub repository.

This summary is based on available prior conversation context. The original challenge statement should be treated as authoritative wherever its wording differs.

### Candidate verification

Before submission, verify each requirement against the original challenge instructions and the actual repository. Record incomplete requirements honestly.

## Additional prompt records

Add further records for recoverable prompts used during implementation, debugging, test development, documentation, and Git operations.

Where exact prompts are available, preserve their original wording. Where only a summary is available, label it as reconstructed.

---

## Record 002 — Database Schema and Relationships (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance designing a relational database for a manufacturing defect traceability and Corrective and Preventive Action (CAPA) system. The database needed entities for products, bills of materials, suppliers, material lots, production orders, machines, process steps, inspection plans, inspection results, defects, corrective actions, and related history.

The work involved primary keys, foreign keys, relationship cardinality, data integrity, and traceability across manufacturing records.

### Candidate verification

The candidate should compare the implemented schema with the original challenge brief and understand the purpose of the relationships and constraints.

## Record 003 — Synthetic Data Generation (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance implementing deterministic synthetic manufacturing data generation with seed `20261022`, configurable dataset scale, and the required product, supplier, material lot, production order, and inspection volumes. The work also involved labelled edge cases and a separate ground-truth file.

### Candidate verification

The candidate should verify generated row counts, reproducibility, anomaly labels, and whether ground-truth labels are kept separate from normal detection inputs.

## Record 004 — Anomaly Detection and Data Validation (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance implementing manufacturing data-quality and traceability checks, including invalid material-lot references, missing BOM material consumption, CAPA closure before verification, defects exceeding inspected quantities, and broken traceability chains.

### Candidate verification

The candidate ran the validation module and reviewed its output. The recorded validation run reported 7 of 7 checks passing with zero reported issues. The candidate should also understand the limitations of the checks and the separate anomaly-detection tests.

## Record 005 — Automated Tests and Debugging (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance developing and debugging automated tests for data generation, anomaly detection, and validation, while avoiding unintended changes to the main project database during tests.

### Candidate verification

The candidate ran `python -m pytest -v`. The recorded run reported 11 tests passed. This result applies to the tests in the repository at the time of the run.

## Record 006 — Data Exports and Reproducibility (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance exporting manufacturing records to CSV, JSON, and SQL formats and documenting export metadata, record counts, and file checksums.

### Candidate verification

The candidate should verify that the exported files exist, that the manifest reflects the intended dataset, and that checksums can be independently checked.

## Record 007 — Dashboard and Defect Traceability (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-27
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance improving the Streamlit manufacturing dashboard and defect traceability output, including displaying related corrective-action details such as CAPA ID, action description, status, opened and closed dates, and verification result.

### Candidate verification

The candidate compiled the modified Python modules, ran the test suite, and inspected the dashboard. The candidate should confirm the displayed information against the underlying database records.

## Record 008 — README and Repository Documentation (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-26 to 2026-10-27
**Original wording:** Not fully recovered

### Prompt summary

Requested assistance improving the project README, setup instructions, project structure, feature descriptions, verification steps, AI usage disclosure, and repository presentation.

### Candidate verification

The candidate should ensure that the README describes only implemented and verified features and that the setup and run commands work in a clean environment.

## Record 009 — Git and Submission Preparation (Reconstructed)

**Tool:** ChatGPT
**Record type:** Reconstructed summary; not verbatim
**Date:** 2026-10-27
**Original wording:** Not fully recovered

### Prompt summary

Requested step-by-step assistance committing and pushing project changes to the public GitHub repository and checking the repository's final status before submission.

### Candidate verification

The candidate ran Git commands and verified that the latest changes were pushed and the working tree was clean.

---

## AI Usage Disclosure

**AI tool used:** ChatGPT only, as reported by the candidate.

### Where ChatGPT assisted

ChatGPT assisted with project planning, database and code implementation discussions, debugging, automated testing, data exports, dashboard improvements, README documentation, and Git workflow guidance.

### Candidate's verification work

The candidate executed project commands locally, inspected command output, ran data validation, ran the automated tests, checked exports, inspected the dashboard, and committed and pushed repository changes.

Recorded verification results include:

- Data validation: 7 of 7 checks passed, with zero reported issues.
- Automated tests: 11 passed.
- Git working tree: clean and up to date with `origin/main`.

These checks provide evidence of the tested behavior; they do not prove that every challenge requirement or every possible edge case is covered.

### Limitations and transparency

This document contains reconstructed summaries, not a complete verbatim transcript of the original prompts. The candidate should recover and add exact original prompts from available ChatGPT conversation history wherever possible.

Do not present reconstructed wording as verbatim history. Do not claim that code was independently written or fully understood unless that is accurate. The candidate should be prepared to explain the database design, detection rules, tests, trade-offs, and limitations during the technical interview.
