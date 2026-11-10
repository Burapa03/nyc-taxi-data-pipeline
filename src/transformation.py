
import duckdb
import pandas as pd

from config.settings import START_DATE, END_DATE


def process_source_file(con, source):
    """
    Process one NYC TLC Parquet file.

    Returns:
        audit_record: Data quality statistics
        curated_record: Standardized monthly trip count
    """

    taxi_type = source["taxi_type"]
    pickup_column = source["pickup_column"]
    source_url = source["source_url"]

    # Pickup column comes from our trusted configuration.
    pickup_expression = f'TRY_CAST("{pickup_column}" AS TIMESTAMP)'

    query = f"""
        WITH parsed_data AS (
            SELECT
                {pickup_expression} AS pickup_ts
            FROM read_parquet(?)
        )

        SELECT
            COUNT(*) AS raw_rows,

            COUNT(*) FILTER (
                WHERE pickup_ts IS NULL
            ) AS null_pickup_rows,

            COUNT(*) FILTER (
                WHERE pickup_ts IS NOT NULL
                AND (
                    pickup_ts < CAST(? AS TIMESTAMP)
                    OR pickup_ts >= CAST(? AS TIMESTAMP)
                )
            ) AS outside_period_rows,

            COUNT(*) FILTER (
                WHERE pickup_ts >= CAST(? AS TIMESTAMP)
                AND pickup_ts < CAST(? AS TIMESTAMP)
            ) AS valid_trip_rows

        FROM parsed_data
    """

    result = con.execute(
        query,
        [
            source_url,
            START_DATE,
            END_DATE,
            START_DATE,
            END_DATE
        ]
    ).fetchone()

    raw_rows, null_rows, outside_rows, valid_rows = result

    # Data quality audit record
    audit_record = {
        "taxi_type": taxi_type,
        "source_month": source["source_month"],
        "raw_rows": raw_rows,
        "null_pickup_rows": null_rows,
        "outside_period_rows": outside_rows,
        "valid_trip_rows": valid_rows
    }

    # Standardized curated record
    curated_record = {
        "taxi_type": taxi_type,
        "year": source["year"],
        "month": source["month"],
        "trip_count": valid_rows
    }

    return audit_record, curated_record


def transform_all_sources(con, manifest):
    """
    Process all source files and integrate
    their results into a common schema.
    """

    audit_records = []
    curated_records = []

    for index, source in manifest.iterrows():

        print(
            f"Processing {index + 1}/{len(manifest)}: "
            f"{source['taxi_type']} - "
            f"{source['source_month']}"
        )

        audit, curated = process_source_file(
            con,
            source
        )

        audit_records.append(audit)
        curated_records.append(curated)

    audit_df = pd.DataFrame(audit_records)
    curated_df = pd.DataFrame(curated_records)

    return audit_df, curated_df
