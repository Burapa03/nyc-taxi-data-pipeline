# NYC Taxi - Data Lifecycle & Reproducible Pipeline

## 1. Project Overview

This project develops a reproducible data pipeline using NYC Taxi and For-Hire Vehicle (FHV) trip records from January to June 2024.

The pipeline processes four taxi types, validates data quality, creates a curated monthly dataset, and analyzes taxi usage to answer the research question:

**Which taxi type was the most used in the first half of 2024?**

The pipeline uses Python, Pandas, and DuckDB to process Parquet files directly from the NYC Taxi and Limousine Commission (TLC) data repository.

It also generates data quality reports, analysis results, and pipeline execution status.

## 2. Research Question

Which taxi type was the most used in the first half of 2024?

The analysis compares the number of valid records for four taxi types:

- Yellow Taxi
- Green Taxi
- FHV
- HVFHV

The analysis period is January 1, 2024, to June 30, 2024.

A valid record is defined as a source record with a non-null pickup datetime within the analysis period.

## 3. Data Source

**Source:** [NYC Taxi and Limousine Commission - Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

- Data format: Parquet
- Period: January-June 2024
- Taxi types: Yellow Taxi, Green Taxi, FHV, and HVFHV
- Total source files: 24 (4 taxi types x 6 months)

The pipeline generates a source manifest containing the expected source files and their corresponding pickup datetime columns.

Source files are accessed directly from the TLC CloudFront data repository using DuckDB and its HTTP file system extension.

## 4. Pipeline Architecture

See [Pipeline Diagram](docs/pipeline_diagram.md).

The pipeline consists of the following stages:

1. Build the source manifest.
2. Inspect source schemas.
3. Read and transform source Parquet files.
4. Validate data quality.
5. Save the curated monthly dataset.
6. Analyze taxi usage and generate reports.

## 5. Technologies

- Python 3.14.10
- Pandas
- DuckDB 1.4.5
- Pytest
- Git and GitHub

Python dependencies are listed in `requirements.txt`.

## 6. Project Structure

```text
nyc-taxi-data-pipeline/
|
|-- config/
|   |-- __init__.py
|   |-- settings.py
|
|-- data/
|   |-- raw/
|   |-- curated/
|
|-- docs/
|   |-- evidence/
|   |   |-- analysis_summary.csv
|   |   |-- data_quality_audit.csv
|   |   |-- data_quality_report.csv
|   |   |-- monthly_trip_counts.csv
|   |   |-- pipeline_summary.json
|   |   |-- schema_report.csv
|   |   |-- source_manifest.csv
|   |
|   |-- pipeline_diagram.md
|
|-- reports/
|
|-- src/
|   |-- __init__.py
|   |-- ingestion.py
|   |-- validation.py
|   |-- transformation.py
|   |-- analysis.py
|   |-- pipeline.py
|
|-- tests/
|   |-- test_pipeline.py
|
|-- requirements.txt
|-- .gitignore
|-- README.md
```

Note: Raw data, generated curated data, and runtime reports are not committed to the repository. Selected execution evidence is stored in `docs/evidence/`.

## 7. Installation

### Prerequisites

- Python 3.14.10 (version used for testing)
- Git
- Internet connection to access NYC TLC Parquet files

### Clone the repository

```bash
git clone https://github.com/Burapa03/nyc-taxi-data-pipeline.git
cd nyc-taxi-data-pipeline
```

### Create a virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 8. Run the Pipeline

Run the complete pipeline from the project root:

```bash
python -m src.pipeline
```

The pipeline performs a full refresh. Each execution processes all 24 configured source files again.

The pipeline generates the following outputs:

| Output | Description |
|---|---|
| `data/curated/monthly_trip_counts.csv` | Monthly trip counts by taxi type |
| `reports/source_manifest.csv` | List of expected source files |
| `reports/schema_report.csv` | Source schema inspection results |
| `reports/data_quality_audit.csv` | Row-level count audit by source file |
| `reports/data_quality_report.csv` | Summary of data quality checks |
| `reports/analysis_summary.csv` | Final taxi usage ranking |
| `reports/pipeline_summary.json` | Execution status and final result |
| `reports/pipeline.log` | Pipeline execution log |

The curated dataset contains 24 records: one record for each taxi type and month.

## 9. Data Quality Validation

The pipeline performs the following data quality checks:

1. **Source file count:** Verifies that all 24 expected source files are included.
2. **Duplicate source records:** Detects duplicate taxi type and source month combinations.
3. **Negative or missing row counts:** Checks that row counts are present and non-negative.
4. **Row accounting:** Verifies that raw rows are accounted for as null pickup datetime rows, out-of-period rows, or valid trip rows.
5. **Taxi type coverage:** Checks that all four expected taxi types are present.
6. **Monthly coverage:** Verifies that all six months from January to June 2024 are included.

The pipeline also inspects the schema of all 24 source files and verifies that each file contains its expected pickup datetime column.

## 10. Results

The pipeline successfully processed 24 source files and generated 24 curated monthly records.

### Taxi Usage Summary

| Rank | Taxi Type | Total Trips | Percentage |
|---:|---|---:|---:|
| 1 | HVFHV | 120,864,668 | 80.76% |
| 2 | Yellow Taxi | 20,332,054 | 13.59% |
| 3 | FHV | 8,119,228 | 5.43% |
| 4 | Green Taxi | 339,801 | 0.23% |
| | **Total** | **149,655,751** | **100.00%** |

**Answer:** HVFHV was the most used taxi type in the first half of 2024, with 120,864,668 valid records, representing approximately 80.76% of all valid records.

Detailed results and execution evidence are available in [`docs/evidence/`](docs/evidence/).

## 11. Automated Tests

Run the test suite:

```bash
python -m pytest -v
```

The test suite contains seven tests:

1. Valid data quality audit passes.
2. Incomplete source data is rejected.
3. Row accounting errors are detected.
4. Taxi usage ranking is correct.
5. Negative trip counts are rejected.
6. Duplicate source records are detected.
7. Missing row counts are detected.

## 12. Design Decisions

### Decision 1: Use DuckDB to process Parquet files

DuckDB can query Parquet files directly without loading the entire trip-level dataset into Pandas first.

This approach reduces unnecessary data movement and is suitable for processing large datasets.

### Decision 2: Create a monthly curated dataset

Instead of storing all raw trip-level records, the pipeline stores aggregated trip counts by taxi type and month.

This produces a smaller dataset that is easier to analyze while preserving monthly information.

### Decision 3: Separate pipeline stages

Ingestion, transformation, validation, analysis, and orchestration are implemented in separate modules.

This improves code organization, maintainability, and testability.


## 13. Comparison with Submission 1

Submission 1 focused on exploring and analyzing NYC Taxi data using a notebook to answer the original research question.

Submission 2 extends the baseline analysis into a reproducible data pipeline with automated ingestion, transformation, data quality validation, curated output, analysis, and execution monitoring.

### Baseline Result Comparison

| Taxi Type | Submission 1 | Submission 2 |
|---|---:|---:|
| HVFHV | 120,864,668 | 120,864,668 |
| Yellow Taxi | 20,332,054 | 20,332,054 |
| FHV | 8,119,228 | 8,119,228 |
| Green Taxi | 339,801 | 339,801 |

The results are consistent across both submissions. HVFHV remains the most used taxi type in the first half of 2024, with 120,864,668 records.

### Improvements in Submission 2

- Automated source manifest generation for 24 Parquet files.
- Schema inspection across all 24 source files.
- Automated data transformation and monthly aggregation.
- Dynamic data quality validation based on configured taxi types and months.
- Detection of duplicate source records and missing row counts.
- Curated monthly output for downstream analysis.
- Automated analysis, execution status, and logging.
- Seven unit tests covering validation and analysis logic.

Submission 1 established the analytical baseline, while Submission 2 improves reproducibility, maintainability, and data quality monitoring.


## 14. Limitations

- The pipeline requires an internet connection and depends on the availability of the NYC TLC CloudFront data repository.
- Temporary HTTP 403 errors may interrupt access to source files.
- The pipeline performs a full refresh rather than incremental processing.
- Schema inspection checks all 24 configured source files, but only verifies the expected pickup datetime column and does not validate the semantic correctness of every column.
- The analysis uses valid record counts as the measure of taxi usage.
- The current validation rules are designed around four taxi types and a six-month study period.
- Data quality checks do not establish whether every source record represents a completed passenger journey.
- Unit tests use synthetic data for validation and analysis logic; they do not replace integration tests against every source file.

## 15. Learning Reflection

This project helped me understand how to turn a one-time data analysis into a reproducible data pipeline. I learned to separate ingestion, transformation, validation, and analysis into independent modules. I also gained practical experience with DuckDB, Parquet files, automated testing, and data quality checks. One important lesson was that a pipeline must handle not only data processing but also source availability and execution failures.
