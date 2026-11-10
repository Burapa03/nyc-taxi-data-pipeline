
import pandas as pd
import duckdb

from config.settings import (
    YEAR,
    MONTHS,
    TAXI_CONFIG,
    BASE_URL
)


def build_source_manifest():
    """
    Create a manifest containing all NYC TLC source files.
    """

    source_records = []

    for taxi_type, config in TAXI_CONFIG.items():

        for month in MONTHS:

            month_str = f"{YEAR}-{month:02d}"

            url = (
                f"{BASE_URL}/"
                f"{config['file_prefix']}_{month_str}.parquet"
            )

            source_records.append({
                "taxi_type": taxi_type,
                "year": YEAR,
                "month": month,
                "source_month": month_str,
                "pickup_column": config["pickup_column"],
                "source_url": url
            })

    manifest = pd.DataFrame(source_records)

    # Validate the source manifest
    expected_files = len(TAXI_CONFIG) * len(MONTHS)

    if len(manifest) != expected_files:
        raise ValueError("Incomplete source manifest")

    if manifest["source_url"].duplicated().any():
        raise ValueError("Duplicate source URLs found")

    return manifest


def create_duckdb_connection():
    """
    Create DuckDB connection and enable HTTP file access.
    """

    con = duckdb.connect()

    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")

    return con


def inspect_source_schemas(con, manifest):
    """
    Inspect one sample file for each taxi type.
    """

    schema_results = []

    sample_files = manifest[
        manifest["month"] == min(MONTHS)
    ]

    for _, source in sample_files.iterrows():

        schema = con.execute(
            """
            DESCRIBE
            SELECT *
            FROM read_parquet(?)
            """,
            [source["source_url"]]
        ).df()

        pickup_column = source["pickup_column"]

        schema_results.append({
            "taxi_type": source["taxi_type"],
            "number_of_columns": len(schema),
            "pickup_column": pickup_column,
            "pickup_column_found":
                pickup_column in schema["column_name"].tolist()
        })

    schema_df = pd.DataFrame(schema_results)

    if not schema_df["pickup_column_found"].all():
        raise ValueError(
            "Required pickup datetime column is missing"
        )

    return schema_df
