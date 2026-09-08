"""Automated tests for ExpiryAware recommendation engine rules, scoring, and priority bands."""
from datetime import date
from app.recommender import (
    evaluate_batch,
    score_expiry,
    score_surplus,
    score_demand,
    score_location,
)


def test_rule_1_expiry_urgency():
    """RULE 1: If days_to_expiry <= 30: increase expiry urgency."""
    score_30d, urgency_30d = score_expiry(20)
    score_90d, urgency_90d = score_expiry(95)

    assert score_30d >= 85.0
    assert urgency_30d in ("HIGH", "CRITICAL")
    assert score_90d < score_30d


def test_rule_2_source_surplus_detection():
    """RULE 2: If source quantity > expected source demand: mark source as surplus."""
    # 20 days left * 1.0 demand/day = 20 expected demand. Stock is 100 -> surplus is 80
    score, surplus_qty, is_surplus = score_surplus(quantity=100.0, days_to_expiry=20, avg_daily_demand=1.0)
    assert is_surplus is True
    assert surplus_qty == 80.0
    assert score >= 70.0

    # 20 days left * 5.0 demand/day = 100 expected demand. Stock is 100 -> surplus is 0
    score_zero, surplus_zero, is_surplus_zero = score_surplus(quantity=100.0, days_to_expiry=20, avg_daily_demand=5.0)
    assert is_surplus_zero is False
    assert surplus_zero == 0.0


def test_rule_3_destination_eligibility():
    """RULE 3: If destination demand > 0: destination is eligible."""
    score_active, cap_active, level_active = score_demand(days_to_expiry=20, dest_demand=4.0, surplus_qty=60.0)
    assert score_active > 0
    assert cap_active == 80.0
    assert level_active == "HIGH"

    score_zero, cap_zero, level_zero = score_demand(days_to_expiry=20, dest_demand=0.0, surplus_qty=60.0)
    assert score_zero == 0.0
    assert cap_zero == 0.0
    assert level_zero == "NONE"


def test_rule_4_distance_feasibility():
    """RULE 4: If transfer distance <= 100 km: location feasibility is high."""
    score_near, label_near = score_location(distance_km=45.0, temperature_sensitive=False)
    score_far, label_far = score_location(distance_km=280.0, temperature_sensitive=False)

    assert score_near >= 85.0
    assert "HIGH" in label_near or "EXCELLENT" in label_near
    assert score_far < 40.0


def test_case_5_rule_8_transfer_capped_to_demand():
    """CASE 5 (RULE 8): Never recommend transferring more than destination demand requires."""
    today = date(2026, 9, 1)
    # Available surplus is 85, but destination can only absorb 30 units (15 days * 2.0/day)
    record = {
        "batch_id": "EDGE-005",
        "medicine_code": "MED-D04",
        "source_location": "Clinic-D",
        "quantity": 100.0,
        "unit_value": 310.0,
        "expiry_date": "2026-09-16",  # 15 days
        "avg_daily_demand": 1.0,      # 15 days * 1.0 = 15 local need -> 85 surplus
        "destination_location": "Clinic-E",
        "destination_daily_demand": 2.0,  # 15 days * 2.0 = 30 capacity
        "transfer_distance_km": 65.0,
        "temperature_sensitive": True,
        "data_quality_score": 98.0,
    }
    rec = evaluate_batch(record, reference_date=today)
    assert rec["recommended_transfer_quantity"] == 30.0
    assert rec["recommended_transfer_quantity"] <= 30.0
    assert any("RULE 8" in r for r in rec["rules_triggered"])


def test_case_6_long_distance_penalty():
    """CASE 6: Very long distance incurs low location score and cold-chain penalty."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-006",
        "medicine_code": "MED-F06",
        "source_location": "Clinic-A",
        "quantity": 70.0,
        "unit_value": 295.0,
        "expiry_date": "2026-09-19",
        "avg_daily_demand": 0.5,
        "destination_location": "Clinic-E",
        "destination_daily_demand": 4.0,
        "transfer_distance_km": 290.0,  # Long distance
        "temperature_sensitive": True,  # Cold chain penalty applies
        "data_quality_score": 92.0,
    }
    rec = evaluate_batch(record, reference_date=today)
    assert rec["location_score"] <= 20.0
    assert rec["evidence"]["temperature_control"] == "Cold Chain (2-8°C)"


def test_case_7_high_risk_zero_destination_demand():
    """CASE 7: Near expiry risk but zero destination demand results in 0 transfer quantity."""
    today = date(2026, 9, 1)
    record = {
        "batch_id": "EDGE-007",
        "medicine_code": "MED-I09",
        "source_location": "Clinic-B",
        "quantity": 50.0,
        "unit_value": 450.0,
        "expiry_date": "2026-09-13",  # 12 days
        "avg_daily_demand": 0.5,
        "destination_location": "Clinic-C",
        "destination_daily_demand": 0.0,  # Zero demand
        "transfer_distance_km": 38.0,
        "temperature_sensitive": True,
        "data_quality_score": 94.0,
    }
    rec = evaluate_batch(record, reference_date=today)
    assert rec["recommended_transfer_quantity"] == 0.0
    assert rec["priority"] == "NO ACTION"


def test_priority_bands():
    """Verify priority band classification based on risk score."""
    today = date(2026, 9, 1)
    # High priority case: near expiry, big surplus, high demand, near distance, high quality
    rec_high = evaluate_batch({
        "batch_id": "REC-HIGH",
        "medicine_code": "MED-A01",
        "source_location": "Clinic-A",
        "quantity": 120.0,
        "unit_value": 300.0,
        "expiry_date": "2026-09-15",  # 14 days
        "avg_daily_demand": 0.5,
        "destination_location": "Clinic-B",
        "destination_daily_demand": 8.0,
        "transfer_distance_km": 24.0,
        "temperature_sensitive": False,
        "data_quality_score": 98.0,
    }, reference_date=today)

    assert rec_high["risk_score"] >= 80.0
    assert rec_high["priority"] == "HIGH PRIORITY"
    assert rec_high["confidence_level"] == "HIGH CONFIDENCE"
