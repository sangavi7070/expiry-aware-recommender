"""Automated tests for ExpiryAware data validation engine and edge cases.

TECHNICAL TEST DOCUMENTATION - GROUP C: VALIDATION TESTS & SAFETY BOUNDARIES
=============================================================================
This suite validates the strict clinical data validation rules governing batch ingestion.
Records are classified into three deterministic integrity tiers:
  1. VALID   -> Clean clinical data; proceed to full recommendation scoring.
  2. WARNING -> Minor missing optional context (e.g. demand); reduce confidence score.
  3. BLOCKED -> Critical clinical field missing or corrupted; immediately halt recommendations.

Safety Philosophy: The system fails closed on physical impossibilities and missing dates.
"""
from datetime import date, timedelta
from app.validation import validate_inventory_record
from app.recommender import evaluate_batch


def test_valid_record():
    """Verify that a complete, normal record validates successfully as VALID.

    - What is being tested: End-to-end clinical record validation for clean, complete batch inputs.
    - Input condition: All 13 fields populated with physiologically and logistically sound values
      (Batch BATCH-TEST-01, MED-A01, quantity 100, unit value $385, valid future expiry, active demand).
    - Expected behaviour: Validator assigns status='VALID' with 0 error/warning reasons.
    - Safety boundary: Valid records proceed through recommendation scoring without safety penalties.
    - Expected system response: result.status == 'VALID', len(result.reasons) == 0.
    - Why the test matters: Establishes the operational control baseline for acceptable clinical inventory.
    """
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
    """CASE 1: Missing Expiry Date Safety Boundary (Rule 5).

    - What is being tested: Fail-closed boundary when expiration date is absent or empty.
    - Input condition: Batch EDGE-001 with empty string expiry_date="".
    - Expected behaviour: Validation status immediately flags 'BLOCKED'; recommendation engine halts,
      sets transfer quantity to 0.0, confidence to 0.0, and records Rule 5 trigger.
    - Safety boundary: Missing expiry date MUST block safe redistribution because urgency cannot be calculated.
    - Expected system response: val.status == 'BLOCKED', rec['status'] == 'BLOCKED', rec['recommended_transfer_quantity'] == 0.0.
    - Why the test matters: Prevents unverified or potentially expired medicines from entering transit.
    """
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
    """CASE 2: Negative Quantity Safety Boundary (Rule 6).

    - What is being tested: Defense against corrupted inventory balances (quantity < 0).
    - Input condition: Batch EDGE-002 with physical quantity = -25.0 units.
    - Expected behaviour: Validator halts record with status='BLOCKED'; flags negative_quantity=True;
      recommender outputs status='BLOCKED' and recommended_transfer_quantity=0.0.
    - Safety boundary: Non-positive quantities indicate ledger corruption; cannot physically redistribute negative stock.
    - Expected system response: val.status == 'BLOCKED', val.flags['negative_quantity'] == True, rec['status'] == 'BLOCKED'.
    - Why the test matters: Prevents mathematical inversion errors and phantom courier dispatch requests.
    """
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
    """CASE 3: Missing Destination Demand Uncertainty Handling (Rule 7).

    - What is being tested: Graceful uncertainty degradation when recipient consumption data is unrecorded.
    - Input condition: Batch EDGE-003 with destination_daily_demand=None.
    - Expected behaviour: System does NOT crash or block completely; instead emits status='WARNING',
      reduces recommendation confidence by 25 points, and records Rule 7 advisory.
    - Safety boundary: Uncertainty must be explicitly communicated without halting all clinical visibility.
    - Expected system response: val.status == 'WARNING', rec['status'] == 'WARNING', rec['confidence'] < 80.0.
    - Why the test matters: Balances patient safety with operational continuity by alerting staff to missing data.
    """
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
    """CASE 4: Already Expired Medicine Absolute Prohibition (Rule 9).

    - What is being tested: Absolute safety constraint against redistributing expired stock.
    - Input condition: Batch EDGE-004 expired 12 days ago (expiry_date='2026-08-20' with today='2026-09-01').
    - Expected behaviour: Validator sets status='BLOCKED'; flags already_expired=True; recommender sets
      status='BLOCKED', transfer quantity to 0.0, and records Rule 9 safety trigger.
    - Safety boundary: Expired pharmaceuticals are legally and clinically unfit for patient administration.
    - Expected system response: val.status == 'BLOCKED', rec['status'] == 'BLOCKED', rec['recommended_transfer_quantity'] == 0.0.
    - Why the test matters: Regulatory compliance and clinical patient safety; zero-tolerance for expired dispatch.
    """
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
    """Boundary Case: Zero Quantity Stock Ledger Entry.

    - What is being tested: Handling of depleted stock records where quantity == 0.0.
    - Input condition: Batch EDGE-ZERO with quantity = 0.0.
    - Expected behaviour: Validator sets status='BLOCKED' and sets flag zero_quantity=True.
    - Safety boundary: Depleted batches have no physical units available to transfer.
    - Expected system response: val.status == 'BLOCKED', val.flags['zero_quantity'] is True.
    - Why the test matters: Prevents zero-unit transfer orders from cluttering pharmacist approval workflows.
    """
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
    """Boundary Case: Negative Financial Valuation Entry.

    - What is being tested: Defense against negative drug acquisition costs (unit_value < 0).
    - Input condition: Batch EDGE-NEGVAL with unit_value = -10.0.
    - Expected behaviour: Validator halts record with status='BLOCKED' and flags negative_unit_value=True.
    - Safety boundary: Financial metrics cannot accommodate negative acquisition values.
    - Expected system response: val.status == 'BLOCKED', val.flags['negative_unit_value'] is True.
    - Why the test matters: Protects downstream financial reporting and protected-value calculations from corruption.
    """
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
