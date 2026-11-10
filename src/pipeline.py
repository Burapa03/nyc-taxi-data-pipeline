
import json
import logging
import time

from datetime import datetime, timezone

from config.settings import (
    RAW_DIR,
    CURATED_DIR,
    REPORT_DIR
)

from src.ingestion import (
    build_source_manifest,
    create_duckdb_connection,
    inspect_source_schemas
)

from src.transformation import transform_all_sources
from src.validation import validate_audit

from src.analysis import (
    analyze_curated_data,
    save_analysis_result
)


def setup_logging():
    """
    Configure console and file logging.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                REPORT_DIR / "pipeline.log",
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ],
        force=True
    )


def save_pipeline_status(status):
    """
    Save pipeline execution status as JSON.
    """

    output_path = REPORT_DIR / "pipeline_summary.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            status,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )


def run_pipeline():
    """
    Execute the complete NYC Taxi data pipeline.
    """

    start_time = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()

    setup_logging()

    logger = logging.getLogger(__name__)

    con = None

    # Initialize output directories
    for directory in [RAW_DIR, CURATED_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    status = {
        "status": "RUNNING",
        "started_at": started_at,
        "finished_at": None,
        "duration_seconds": None,
        "source_files_processed": 0,
        "curated_records": 0,
        "result": None,
        "error": None
    }

    try:

        logger.info("Starting NYC Taxi Data Pipeline")

        # 1. Ingestion
        logger.info("Step 1: Building source manifest")

        manifest = build_source_manifest()

        manifest.to_csv(
            REPORT_DIR / "source_manifest.csv",
            index=False
        )

        logger.info(
            "Found %s source files",
            len(manifest)
        )

        # 2. Schema inspection
        logger.info("Step 2: Inspecting source schemas")

        con = create_duckdb_connection()

        schema_report = inspect_source_schemas(
            con,
            manifest
        )

        schema_report.to_csv(
            REPORT_DIR / "schema_report.csv",
            index=False
        )

        logger.info("Schema inspection passed")

        # 3. Transformation
        logger.info("Step 3: Transforming source data")

        audit, curated = transform_all_sources(
            con,
            manifest
        )

        status["source_files_processed"] = len(curated)
        status["curated_records"] = len(curated)

        # 4. Data quality validation
        logger.info("Step 4: Validating data quality")

        audit, quality_report = validate_audit(audit)

        audit.to_csv(
            REPORT_DIR / "data_quality_audit.csv",
            index=False
        )

        quality_report.to_csv(
            REPORT_DIR / "data_quality_report.csv",
            index=False
        )

        logger.info("Data quality validation passed")

        # 5. Save curated dataset
        logger.info("Step 5: Saving curated dataset")

        curated.to_csv(
            CURATED_DIR / "monthly_trip_counts.csv",
            index=False
        )

        # 6. Analysis
        logger.info("Step 6: Analyzing taxi usage")

        analysis = analyze_curated_data(curated)

        analysis_path = save_analysis_result(analysis)

        winner = analysis.iloc[0]

        status["result"] = {
            "most_used_taxi_type": winner["taxi_type"],
            "total_trips": int(winner["total_trips"]),
            "percentage": float(winner["percentage"]),
            "rank": int(winner["rank"])
        }

        # 7. Complete
        status["status"] = "SUCCESS"

        logger.info(
            "Most used taxi type: %s",
            winner["taxi_type"]
        )

        logger.info(
            "Total trips: %s",
            winner["total_trips"]
        )

        logger.info("Pipeline completed successfully")

    except Exception as error:

        status["status"] = "FAILED"
        status["error"] = str(error)

        logger.exception("Pipeline failed")

        raise

    finally:

        if con is not None:
            con.close()

        status["finished_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        status["duration_seconds"] = round(
            time.perf_counter() - start_time,
            2
        )

        save_pipeline_status(status)

        logger.info(
            "Pipeline status: %s",
            status["status"]
        )

    return status


if __name__ == "__main__":

    run_pipeline()
