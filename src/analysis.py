
import pandas as pd

from config.settings import REPORT_DIR


def analyze_curated_data(curated_df):
    """
    Aggregate monthly trip counts by taxi type,
    calculate percentages, and rank taxi types.
    """

    required_columns = [
        "taxi_type",
        "year",
        "month",
        "trip_count"
    ]

    # Validate input columns
    missing = [
        col for col in required_columns
        if col not in curated_df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if curated_df["trip_count"].isna().any():
        raise ValueError("Missing trip counts detected")

    if (curated_df["trip_count"] < 0).any():
        raise ValueError("Negative trip counts detected")

    # Aggregate monthly counts by taxi type
    summary = (
        curated_df
        .groupby("taxi_type", as_index=False)
        ["trip_count"]
        .sum()
        .rename(columns={"trip_count": "total_trips"})
    )

    # Calculate total trips across all taxi types
    grand_total = summary["total_trips"].sum()

    if grand_total <= 0:
        raise ValueError("Total trips must be positive")

    # Calculate percentage
    summary["percentage"] = (
        summary["total_trips"] / grand_total * 100
    )

    # Rank taxi types by total trips
    summary["rank"] = (
        summary["total_trips"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # Sort from most used to least used
    summary = summary.sort_values(
        "total_trips",
        ascending=False
    ).reset_index(drop=True)

    return summary


def save_analysis_result(summary):
    """
    Save analysis results as a CSV file.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = REPORT_DIR / "analysis_summary.csv"

    summary.to_csv(output_path, index=False)

    return output_path
