"""Automated tests for ExpiryAware data validation engine and edge cases."""
from datetime import date, timedelta
from app.validation import validate_inventory_record
from app.recommender import evaluate_batch


def test_valid_record():
    """Verify that a complete, normal record validates successfully as VALID."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "BATCH-TEST-01",
        "medicine_code": "MED-A01",
        "source_location": "Clinic-A",
        "quantity": 100.0,
        "unit_value": 385.0,
        "expiry_date": "2026-09-25",
        "avg_daily_demand": 1.0,
        "destination_location": "Clinic-B",
        "destination_daily_demand": 4.0,
        "transfer_distance_km": 24.0,
        "temperature_sensitive": True,
        "data_quality_score": 98.0,
    }
    result = validate_inventory_record(record, reference_date=today)
    assert result.status == "VALID"
    assert len(result.reasons) == 0


def test_case_1_missing_expiry_date():
    """CASE 1: Missing expiry date must be BLOCKED (Rule 5)."""
    record = {
        "batch_id": "EDGE-001",
        "medicine_code": "MED-A01",
        "source_location": "Clinic-A",
        "quantity": 80.0,
        "unit_value": 385.0,
        "expiry_date": "",  # Missing expiry date
        "destination_daily_demand": 4.0,
    }
    val = validate_inventory_record(record)
    assert val.status == "BLOCKED"
    assert any("Expiry date is unavailable" in r for r in val.reasons)

    rec = evaluate_batch(record)
    assert rec["status"] == "BLOCKED"
    assert rec["recommended_transfer_quantity"] == 0.0
    assert any("RULE 5" in r for r in rec["rules_triggered"])


def test_case_2_negative_quantity():
    """CASE 2: Negative quantity must be BLOCKED (Rule 6)."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-002",
        "medicine_code": "MED-C03",
        "source_location": "Clinic-B",
        "quantity": -25.0,  # Negative quantity
        "unit_value": 78.5,
        "expiry_date": "2026-09-20",
        "destination_daily_demand": 5.0,
    }
    val = validate_inventory_record(record, reference_date=today)
    assert val.status == "BLOCKED"
    assert val.flags.get("negative_quantity") is True

    rec = evaluate_batch(record, reference_date=today)
    assert rec["status"] == "BLOCKED"
    assert rec["recommended_transfer_quantity"] == 0.0


def test_case_3_missing_destination_demand():
    """CASE 3: Missing destination demand emits WARNING and reduces confidence (Rule 7)."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-003",
        "medicine_code": "MED-E05",
        "source_location": "Clinic-A",
        "quantity": 90.0,
        "unit_value": 42.0,
        "expiry_date": "2026-09-23",
        "destination_daily_demand": None,  # Missing destination demand
        "transfer_distance_km": 24.0,
        "temperature_sensitive": False,
        "data_quality_score": 80.0,
    }
    val = validate_inventory_record(record, reference_date=today)
    assert val.status == "WARNING"
    assert val.flags.get("missing_destination_demand") is True

    rec = evaluate_batch(record, reference_date=today)
    assert rec["status"] == "WARNING"
    # Confidence should be penalized for missing demand
    assert rec["confidence"] < 80.0
    assert any("RULE 7" in r for r in rec["rules_triggered"])


def test_case_4_already_expired_batch():
    """CASE 4: Already expired batch must be BLOCKED / NO TRANSFER (Rule 9)."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-004",
        "medicine_code": "MED-B02",
        "source_location": "Clinic-C",
        "quantity": 40.0,
        "unit_value": 420.0,
        "expiry_date": "2026-08-20",  # Expired 12 days ago
        "destination_daily_demand": 3.0,
    }
    val = validate_inventory_record(record, reference_date=today)
    assert val.status == "BLOCKED"
    assert val.flags.get("already_expired") is True

    rec = evaluate_batch(record, reference_date=today)
    assert rec["status"] == "BLOCKED"
    assert rec["recommended_transfer_quantity"] == 0.0
    assert any("RULE 9" in r for r in rec["rules_triggered"])


def test_zero_quantity():
    """Zero quantity must be BLOCKED from transfer."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-ZERO",
        "medicine_code": "MED-A01",
        "source_location": "Clinic-A",
        "quantity": 0.0,
        "unit_value": 100.0,
        "expiry_date": "2026-09-25",
        "destination_daily_demand": 2.0,
    }
    val = validate_inventory_record(record, reference_date=today)
    assert val.status == "BLOCKED"
    assert val.flags.get("zero_quantity") is True


def test_negative_unit_value():
    """Negative unit value must trigger a BLOCKED state."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-NEGVAL",
        "medicine_code": "MED-A01",
        "source_location": "Clinic-A",
        "quantity": 50.0,
        "unit_value": -10.0,
        "expiry_date": "2026-09-25",
    }
    val = validate_inventory_record(record, reference_date=today)
    assert val.status == "BLOCKED"
    assert val.flags.get("negative_unit_value") is True
