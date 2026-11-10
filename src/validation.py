
import pandas as pd

from config.settings import TAXI_CONFIG, MONTHS, YEAR


def validate_audit(audit_df):
    required_columns = [
        "taxi_type",
        "source_month",
        "raw_rows",
        "null_pickup_rows",
        "outside_period_rows",
        "valid_trip_rows"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in audit_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    audit_df = audit_df.copy()

    # Derive expected sources from configuration
    expected_types = set(TAXI_CONFIG.keys())
    expected_months = {
        f"{YEAR}-{month:02d}" for month in MONTHS
    }

    expected_file_count = (
        len(expected_types) * len(expected_months)
    )

    # Check source file count
    if len(audit_df) != expected_file_count:
        raise ValueError(
            f"Expected {expected_file_count} files, "
            f"got {len(audit_df)}"
        )

    # Check duplicate source records
    if audit_df.duplicated(
        subset=["taxi_type", "source_month"]
    ).any():
        raise ValueError("Duplicate source records found")

    # Check taxi type coverage
    actual_types = set(audit_df["taxi_type"])

    if actual_types != expected_types:
        raise ValueError(
            "Missing or unexpected taxi types"
        )

    # Check monthly coverage for every taxi type
    for taxi_type in expected_types:
        monthly_data = audit_df[
            audit_df["taxi_type"] == taxi_type
        ]

        actual_months = set(monthly_data["source_month"])

        if actual_months != expected_months:
            raise ValueError(
                f"Incorrect monthly coverage for {taxi_type}"
            )

    # Check row counts
    count_columns = [
        "raw_rows",
        "null_pickup_rows",
        "outside_period_rows",
        "valid_trip_rows"
    ]

    if audit_df[count_columns].isna().any().any():
        raise ValueError("Missing row counts detected")

    if (audit_df[count_columns] < 0).any().any():
        raise ValueError("Negative row counts detected")

    # Check row accounting
    audit_df["unaccounted_rows"] = (
        audit_df["raw_rows"]
        - audit_df["null_pickup_rows"]
        - audit_df["outside_period_rows"]
        - audit_df["valid_trip_rows"]
    )

    if (audit_df["unaccounted_rows"] != 0).any():
        raise ValueError("Some rows were not accounted for")

    # Generate data quality report
    quality_results = [
        {
            "check": "Source file count",
            "status": "PASS",
            "details": (
                f"{len(audit_df)} of "
                f"{expected_file_count} expected files processed"
            )
        },
        {
            "check": "Duplicate source records",
            "status": "PASS",
            "details": "No duplicate taxi type/month records"
        },
        {
            "check": "Negative or missing row counts",
            "status": "PASS",
            "details": "All row counts are present and non-negative"
        },
        {
            "check": "Row accounting",
            "status": "PASS",
            "details": "All rows accounted for"
        },
        {
            "check": "Taxi type coverage",
            "status": "PASS",
            "details": f"All {len(expected_types)} taxi types found"
        },
        {
            "check": "Monthly coverage",
            "status": "PASS",
            "details": (
                f"{len(expected_months)} months per taxi type"
            )
        }
    ]

    quality_report = pd.DataFrame(quality_results)

    return audit_df, quality_report
