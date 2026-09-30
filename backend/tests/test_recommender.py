"""Automated tests for ExpiryAware recommendation engine rules, scoring, and priority bands.

TECHNICAL TEST DOCUMENTATION - GROUP B: RECOMMENDATION ENGINE TESTS
===================================================================
This suite validates the core mathematical and heuristic scoring engine enforcing Rules 1-10:
  Risk Score = 0.35 * Expiry + 0.25 * Surplus + 0.25 * Demand + 0.10 * Location + 0.05 * DataQuality

Each test verifies deterministic output, threshold boundaries, quantity capping, and
safe fallback when clinical parameters fail to satisfy transfer eligibility.
"""
from datetime import date
from app.recommender import (
    evaluate_batch,
    score_expiry,
    score_surplus,
    score_demand,
    score_location,
)


def test_rule_1_expiry_urgency():
    """RULE 1: Expiry Urgency Factor Scoring.

    - What is being tested: Expiry urgency scoring function across near-term vs long-term dates.
    - Input condition: 20 days remaining (critical/urgent window) vs 95 days remaining (safe window).
    - Expected behaviour: Batches with days_to_expiry <= 30 receive elevated scores >= 85 and
      'HIGH' or 'CRITICAL' urgency tier; long-dated batches receive substantially lower scores.
    - Safety boundary: Score is monotonically decreasing with days until expiry; never negative.
    - Expected system response: score_30d >= 85.0, urgency in ('HIGH', 'CRITICAL'), score_90d < score_30d.
    - Why the test matters: Ensures near-expiry medicines are surfaced proactively before clinical viability expires.
    """
    score_30d, urgency_30d = score_expiry(20)
    score_90d, urgency_90d = score_expiry(95)

    assert score_30d >= 85.0
    assert urgency_30d in ("HIGH", "CRITICAL")
    assert score_90d < score_30d


def test_rule_2_source_surplus_detection():
    """RULE 2: Source Surplus Detection & Projected Consumption.

    - What is being tested: Identification of true local surplus based on source clinic demand.
    - Input condition:
        Case A: 100 units held, 20 days to expiry, 1.0 units/day local demand -> 20 consumed, 80 surplus.
        Case B: 100 units held, 20 days to expiry, 5.0 units/day local demand -> 100 consumed, 0 surplus.
    - Expected behaviour: Case A flags surplus=True with 80 units; Case B flags surplus=False with 0 units.
    - Safety boundary: Stock that will be consumed locally must NEVER be marked as surplus.
    - Expected system response: is_surplus is True and surplus_qty == 80 for Case A; False and 0 for Case B.
    - Why the test matters: Prevents creating artificial shortages at the source clinic by redistributing
      stock needed for its own scheduled patients.
    """
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
    """RULE 3: Candidate Destination Eligibility & Demand Matching.

    - What is being tested: Destination clinic demand scoring and capacity calculation.
    - Input condition: Active destination demand (4.0 units/day over 20 days = 80 capacity) vs
      zero destination demand (0.0 units/day = 0 capacity).
    - Expected behaviour: Active demand scores > 0 with 'HIGH' level; zero demand yields 0.0 score and 'NONE'.
    - Safety boundary: Clinics without documented active patient demand are strictly ineligible.
    - Expected system response: score_active > 0, cap_active == 80.0; score_zero == 0.0, cap_zero == 0.0.
    - Why the test matters: Eliminates the risk of sending surplus to locations where it will sit unused and expire.
    """
    score_active, cap_active, level_active = score_demand(days_to_expiry=20, dest_demand=4.0, surplus_qty=60.0)
    assert score_active > 0
    assert cap_active == 80.0
    assert level_active == "HIGH"

    score_zero, cap_zero, level_zero = score_demand(days_to_expiry=20, dest_demand=0.0, surplus_qty=60.0)
    assert score_zero == 0.0
    assert cap_zero == 0.0
    assert level_zero == "NONE"


def test_rule_4_distance_feasibility():
    """RULE 4: Transit Logistics Feasibility & Distance Scoring.

    - What is being tested: Distance scoring logic for road transport between clinics.
    - Input condition: Short transit distance (45 km) vs long haul distance (280 km).
    - Expected behaviour: <= 100 km yields high feasibility score (>=85); > 250 km yields low score (<40).
    - Safety boundary: Feasibility score scales inversely with distance; transit constraints prevent delayed shipments.
    - Expected system response: score_near >= 85.0 ('HIGH'/'EXCELLENT'); score_far < 40.0 ('POOR'/'CHALLENGING').
    - Why the test matters: Prioritizes local and regional transfers to ensure timely clinical delivery before expiry.
    """
    score_near, label_near = score_location(distance_km=45.0, temperature_sensitive=False)
    score_far, label_far = score_location(distance_km=280.0, temperature_sensitive=False)

    assert score_near >= 85.0
    assert "HIGH" in label_near or "EXCELLENT" in label_near
    assert score_far < 40.0


def test_case_5_rule_8_transfer_capped_to_demand():
    """CASE 5 (RULE 8): Strict Transfer Quantity Capping to Destination Demand.

    - What is being tested: Enforcement of Rule 8: Transfer Qty = min(Surplus, Destination Capacity, Total Stock).
    - Input condition: Available surplus is 85 units (100 stock - 15 local consumption), but candidate Clinic-E
      can only absorb 30 units (15 days * 2.0 daily demand).
    - Expected behaviour: Recommendation clamps transfer quantity to exactly 30 units, leaving 55 units at source.
    - Safety boundary: Transfer quantity can NEVER exceed the destination clinic's verified absorption capacity.
    - Expected system response: recommended_transfer_quantity == 30.0; Rule 8 explicit trigger recorded in explanation.
    - Why the test matters: Prevents "dumping" excess stock onto another clinic, which would merely relocate waste.
    """
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
    """CASE 6: Cold-Chain Logistics Penalty for Excessive Distance.

    - What is being tested: Location feasibility degradation and cold-chain risk identification.
    - Input condition: 290 km distance for temperature-sensitive biologic (Infliximab, 2°C - 8°C).
    - Expected behaviour: Distance penalty plus 20-point cold-chain surcharge reduces location score <= 20.0.
    - Safety boundary: Long-distance cold-chain transfers must flag risk and lower confidence to prevent spoilage.
    - Expected system response: location_score <= 20.0; temperature_control flags 'Cold Chain (2-8°C)'.
    - Why the test matters: Temperature-sensitive pharmaceuticals degrade rapidly if courier transit exceeds thermal limits.
    """
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
    """CASE 7: Near-Expiry Batch with Zero Destination Demand.

    - What is being tested: Safe zero-transfer fallback when destination has zero consumption rate.
    - Input condition: High urgency (12 days left, Oncology biologic), but candidate Clinic-C demand is 0.0/day.
    - Expected behaviour: System refuses to recommend transfer, sets transfer quantity to 0.0, and assigns NO ACTION.
    - Safety boundary: Never dispatch medicine to a facility without documented clinical need, regardless of expiry urgency.
    - Expected system response: recommended_transfer_quantity == 0.0, priority == 'NO ACTION'.
    - Why the test matters: Protects logistics budget and staff time from futile medicine movements.
    """
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
    """Verify priority band classification based on risk score thresholds.

    - What is being tested: Priority band assignment (HIGH: 80-100, MEDIUM: 60-79, LOW: 40-59, NO ACTION: <40).
    - Input condition: Optimal transfer candidate (14 days to expiry, 113 unit surplus, high demand, 24 km distance).
    - Expected behaviour: Multi-factor formula computes risk_score >= 80.0, yielding 'HIGH PRIORITY'.
    - Safety boundary: Priority bands accurately stratify urgency for pharmacist review queues.
    - Expected system response: risk_score >= 80.0, priority == 'HIGH PRIORITY', confidence_level == 'HIGH CONFIDENCE'.
    - Why the test matters: Enables clinical dispensaries to triage high-value near-expiry transfers immediately.
    """
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
