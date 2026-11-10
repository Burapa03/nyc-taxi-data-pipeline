
import pandas as pd
import pytest

from src.validation import validate_audit
from src.analysis import analyze_curated_data


@pytest.fixture
def sample_audit():
    taxi_types = [
        "Yellow Taxi",
        "Green Taxi",
        "FHV",
        "HVFHV"
    ]

    rows = [
        {
            "taxi_type": taxi_type,
            "source_month": f"2024-{month:02d}",
            "raw_rows": 100,
            "null_pickup_rows": 5,
            "outside_period_rows": 5,
            "valid_trip_rows": 90
        }
        for taxi_type in taxi_types
        for month in range(1, 7)
    ]

    return pd.DataFrame(rows)


def test_valid_audit_passes(sample_audit):
    audit, report = validate_audit(sample_audit)

    assert len(audit) == 24
    assert (report["status"] == "PASS").all()


def test_incomplete_source_fails(sample_audit):
    incomplete = sample_audit.iloc[:-1]

    with pytest.raises(ValueError):
        validate_audit(incomplete)


def test_row_accounting_fails(sample_audit):
    invalid = sample_audit.copy()
    invalid.loc[0, "valid_trip_rows"] = 80

    with pytest.raises(ValueError):
        validate_audit(invalid)


def test_analysis_ranking():
    data = pd.DataFrame({
        "taxi_type": [
            "Yellow Taxi",
            "Green Taxi",
            "FHV",
            "HVFHV"
        ],
        "year": [2024] * 4,
        "month": [1] * 4,
        "trip_count": [
            100,
            10,
            50,
            500
        ]
    })

    result = analyze_curated_data(data)

    assert result.iloc[0]["taxi_type"] == "HVFHV"
    assert result.iloc[0]["rank"] == 1
    assert result.iloc[-1]["taxi_type"] == "Green Taxi"


def test_analysis_rejects_negative_trips():
    data = pd.DataFrame({
        "taxi_type": ["Yellow Taxi"],
        "year": [2024],
        "month": [1],
        "trip_count": [-10]
    })

    with pytest.raises(ValueError):
        analyze_curated_data(data)


def test_duplicate_source_fails(sample_audit):
    invalid = sample_audit.copy()

    # Duplicate the first source record
    invalid.loc[1, "source_month"] = invalid.loc[0, "source_month"]
    invalid.loc[1, "taxi_type"] = invalid.loc[0, "taxi_type"]

    with pytest.raises(ValueError, match="Duplicate"):
        validate_audit(invalid)


def test_missing_row_counts_fail(sample_audit):
    invalid = sample_audit.copy()
    invalid.loc[0, "raw_rows"] = None

    with pytest.raises(ValueError, match="Missing row counts"):
        validate_audit(invalid)
