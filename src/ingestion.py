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
    schema_results = []

    for index, source in manifest.iterrows():
        schema = con.execute(
            """
            DESCRIBE
            SELECT *
            FROM read_parquet(?)
            """,
            [source["source_url"]]
        ).df()

        pickup_column = source["pickup_column"]
        available_columns = schema["column_name"].tolist()

        pickup_column_found = pickup_column in available_columns

        schema_results.append({
            "taxi_type": source["taxi_type"],
            "source_month": source["source_month"],
            "number_of_columns": len(schema),
            "pickup_column": pickup_column,
            "pickup_column_found": pickup_column_found
        })

        if not pickup_column_found:
            raise ValueError(
                f"Missing pickup column '{pickup_column}' "
                f"in {source['taxi_type']} "
                f"for {source['source_month']}"
            )

    schema_df = pd.DataFrame(schema_results)

    if len(schema_df) != len(manifest):
        raise ValueError("Schema inspection did not cover all source files")

    return schema_df