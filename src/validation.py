
import pandas as pd


def validate_audit(audit_df):
    """
    Validate the data quality audit results.

    Each raw row must belong to exactly one category:
    - Null pickup datetime
    - Outside analysis period
    - Valid trip
    """

    required_columns = [
        "taxi_type",
        "source_month",
        "raw_rows",
        "null_pickup_rows",
        "outside_period_rows",
        "valid_trip_rows"
    ]

    # Check required columns
    missing_columns = [
        col for col in required_columns
        if col not in audit_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Check number of processed source files
    if len(audit_df) != 24:
        raise ValueError(
            f"Expected 24 files, got {len(audit_df)}"
        )

    count_columns = [
        "raw_rows",
        "null_pickup_rows",
        "outside_period_rows",
        "valid_trip_rows"
    ]

    # Check negative values
    if (audit_df[count_columns] < 0).any().any():
        raise ValueError(
            "Negative row counts detected"
        )

    # Check row accounting
    audit_df = audit_df.copy()

    audit_df["unaccounted_rows"] = (
        audit_df["raw_rows"]
        - audit_df["null_pickup_rows"]
        - audit_df["outside_period_rows"]
        - audit_df["valid_trip_rows"]
    )

    if (audit_df["unaccounted_rows"] != 0).any():
        raise ValueError(
            "Some rows were not accounted for"
        )

    # Check all taxi types and months are covered
    expected_types = {
        "Yellow Taxi",
        "Green Taxi",
        "FHV",
        "HVFHV"
    }

    if set(audit_df["taxi_type"]) != expected_types:
        raise ValueError(
            "Missing or unexpected taxi types"
        )

    for taxi_type in expected_types:

        monthly_data = audit_df[
            audit_df["taxi_type"] == taxi_type
        ]

        if monthly_data["source_month"].nunique() != 6:
            raise ValueError(
                f"{taxi_type} does not contain 6 months"
            )

    # Generate quality report
    quality_results = [
        {
            "check": "Source file count",
            "status": "PASS",
            "details": f"{len(audit_df)} files processed"
        },
        {
            "check": "Negative row counts",
            "status": "PASS",
            "details": "No negative counts found"
        },
        {
            "check": "Row accounting",
            "status": "PASS",
            "details": "All rows accounted for"
        },
        {
            "check": "Taxi type coverage",
            "status": "PASS",
            "details": "All 4 taxi types found"
        },
        {
            "check": "Monthly coverage",
            "status": "PASS",
            "details": "6 months per taxi type"
        }
    ]

    quality_report = pd.DataFrame(quality_results)

    return audit_df, quality_report
