"""Deterministic synthetic inventory and stakeholder dataset generator for ExpiryAware.

Generates reproducible healthcare datasets without any real patient information.
All medicine codes, clinic names, and clinical identifiers are entirely synthetic.
"""
import os
import json
import random
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from .models import InventoryBatch, Recommendation, AuditLog
from .recommender import evaluate_batch

# Seed for reproducible results
RANDOM_SEED = 42

CLINICS = ["Clinic-A", "Clinic-B", "Clinic-C", "Clinic-D", "Clinic-E"]

MEDICINES = [
    {
        "code": "MED-A01",
        "name": "Pembrolizumab Biosimilar 100mg/4mL",
        "category": "Oncology",
        "unit_value": 385.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-B02",
        "name": "Trastuzumab Monoclonal 440mg",
        "category": "Oncology",
        "unit_value": 420.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-C03",
        "name": "Insulin Glargine 300U/mL Solostar",
        "category": "Endocrine",
        "unit_value": 78.50,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-D04",
        "name": "Adalimumab 40mg/0.8mL Pen",
        "category": "Immunology",
        "unit_value": 310.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-E05",
        "name": "Meropenem IV 1000mg Vial",
        "category": "Critical Anti-Infective",
        "unit_value": 42.00,
        "temperature_sensitive": False,
    },
    {
        "code": "MED-F06",
        "name": "Infliximab Infusion 100mg",
        "category": "Immunology",
        "unit_value": 295.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-G07",
        "name": "Epoetin Alfa 10,000 U/mL",
        "category": "Hematology",
        "unit_value": 115.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-H08",
        "name": "Filgrastim 300mcg/0.5mL Syringe",
        "category": "Hematology",
        "unit_value": 165.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-I09",
        "name": "Rituximab 500mg/50mL Concentrate",
        "category": "Oncology",
        "unit_value": 450.00,
        "temperature_sensitive": True,
    },
    {
        "code": "MED-J10",
        "name": "Vancomycin HCl 1g Powder IV",
        "category": "Critical Anti-Infective",
        "unit_value": 32.50,
        "temperature_sensitive": False,
    },
]

# Fixed pairwise clinic distances in kilometers
CLINIC_DISTANCES = {
    ("Clinic-A", "Clinic-B"): 24.0,
    ("Clinic-A", "Clinic-C"): 58.0,
    ("Clinic-A", "Clinic-D"): 92.0,
    ("Clinic-A", "Clinic-E"): 145.0,
    ("Clinic-B", "Clinic-C"): 38.0,
    ("Clinic-B", "Clinic-D"): 74.0,
    ("Clinic-B", "Clinic-E"): 128.0,
    ("Clinic-C", "Clinic-D"): 46.0,
    ("Clinic-C", "Clinic-E"): 95.0,
    ("Clinic-D", "Clinic-E"): 65.0,
}


def get_distance(loc1: str, loc2: str) -> float:
    if loc1 == loc2:
        return 0.0
    pair = (loc1, loc2)
    rev = (loc2, loc1)
    if pair in CLINIC_DISTANCES:
        return CLINIC_DISTANCES[pair]
    if rev in CLINIC_DISTANCES:
        return CLINIC_DISTANCES[rev]
    return 80.0


def generate_synthetic_inventory(count: int = 110, reference_date: date = None) -> List[Dict[str, Any]]:
    """Generate deterministic synthetic inventory records."""
    if reference_date is None:
        reference_date = date.today()

    rng = random.Random(RANDOM_SEED)
    records: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        batch_id = f"BATCH-{100 + i}"
        med = rng.choice(MEDICINES)
        src = rng.choice(CLINICS)
        other_clinics = [c for c in CLINICS if c != src]
        dest = rng.choice(other_clinics)
        dist = get_distance(src, dest)

        # Distribute expiry categories:
        # ~30% near-expiry (5 to 30 days) - HIGH URGENCY
        # ~40% mid-term (31 to 90 days) - MEDIUM
        # ~25% safe (91 to 300 days) - LOW
        # ~5% special / edge variations
        category_pick = rng.random()
        if category_pick < 0.30:
            days = rng.randint(6, 30)
            qty = rng.randint(40, 160)
            src_demand = round(rng.uniform(0.5, 2.0), 1)  # Low source consumption -> high surplus
            dest_demand = round(rng.uniform(3.0, 7.0), 1)  # High destination demand
            data_quality = round(rng.uniform(92.0, 100.0), 1)
        elif category_pick < 0.70:
            days = rng.randint(31, 89)
            qty = rng.randint(30, 200)
            src_demand = round(rng.uniform(1.0, 3.5), 1)
            dest_demand = round(rng.uniform(2.0, 5.0), 1)
            data_quality = round(rng.uniform(88.0, 98.0), 1)
        elif category_pick < 0.95:
            days = rng.randint(90, 280)
            qty = rng.randint(20, 250)
            src_demand = round(rng.uniform(1.5, 4.0), 1)
            dest_demand = round(rng.uniform(1.0, 3.5), 1)
            data_quality = round(rng.uniform(90.0, 100.0), 1)
        else:
            # Subtle edge case variations within dataset
            days = rng.randint(12, 45)
            qty = rng.randint(50, 180)
            src_demand = round(rng.uniform(0.5, 1.5), 1)
            dest_demand = None if rng.random() < 0.5 else 0.0  # Missing or zero destination demand
            data_quality = round(rng.uniform(65.0, 80.0), 1)

        expiry_date = (reference_date + timedelta(days=days)).isoformat()

        record = {
            "batch_id": batch_id,
            "medicine_code": med["code"],
            "medicine_name": med["name"],
            "medicine_category": med["category"],
            "source_location": src,
            "quantity": float(qty),
            "unit_value": float(med["unit_value"]),
            "expiry_date": expiry_date,
            "avg_daily_demand": src_demand,
            "destination_location": dest,
            "destination_daily_demand": dest_demand,
            "transfer_distance_km": dist,
            "temperature_sensitive": med["temperature_sensitive"],
            "data_quality_score": data_quality,
        }
        records.append(record)

    return records


def generate_edge_cases(reference_date: date = None) -> List[Dict[str, Any]]:
    """Explicitly generate documented failure and edge cases (Cases 1-7)."""
    if reference_date is None:
        reference_date = date.today()

    return [
        {
            # CASE 1: Missing expiry date -> BLOCKED
            "batch_id": "EDGE-001",
            "medicine_code": "MED-A01",
            "medicine_name": "Pembrolizumab Biosimilar 100mg/4mL",
            "medicine_category": "Oncology",
            "source_location": "Clinic-A",
            "quantity": 80.0,
            "unit_value": 385.0,
            "expiry_date": "",  # MISSING
            "avg_daily_demand": 1.0,
            "destination_location": "Clinic-C",
            "destination_daily_demand": 4.0,
            "transfer_distance_km": 58.0,
            "temperature_sensitive": True,
            "data_quality_score": 45.0,
            "expected_outcome": "BLOCKED (Missing expiry date)",
        },
        {
            # CASE 2: Negative quantity -> BLOCKED
            "batch_id": "EDGE-002",
            "medicine_code": "MED-C03",
            "medicine_name": "Insulin Glargine 300U/mL Solostar",
            "medicine_category": "Endocrine",
            "source_location": "Clinic-B",
            "quantity": -25.0,  # NEGATIVE
            "unit_value": 78.5,
            "expiry_date": (reference_date + timedelta(days=20)).isoformat(),
            "avg_daily_demand": 2.0,
            "destination_location": "Clinic-D",
            "destination_daily_demand": 5.0,
            "transfer_distance_km": 74.0,
            "temperature_sensitive": True,
            "data_quality_score": 50.0,
            "expected_outcome": "BLOCKED (Negative quantity)",
        },
        {
            # CASE 3: Missing destination demand -> WARNING + reduced confidence
            "batch_id": "EDGE-003",
            "medicine_code": "MED-E05",
            "medicine_name": "Meropenem IV 1000mg Vial",
            "medicine_category": "Critical Anti-Infective",
            "source_location": "Clinic-A",
            "quantity": 90.0,
            "unit_value": 42.0,
            "expiry_date": (reference_date + timedelta(days=22)).isoformat(),
            "avg_daily_demand": 1.0,
            "destination_location": "Clinic-B",
            "destination_daily_demand": None,  # MISSING DEMAND
            "transfer_distance_km": 24.0,
            "temperature_sensitive": False,
            "data_quality_score": 72.0,
            "expected_outcome": "WARNING (Confidence reduced due to missing demand)",
        },
        {
            # CASE 4: Already expired batch -> NO TRANSFER / BLOCKED
            "batch_id": "EDGE-004",
            "medicine_code": "MED-B02",
            "medicine_name": "Trastuzumab Monoclonal 440mg",
            "medicine_category": "Oncology",
            "source_location": "Clinic-C",
            "quantity": 40.0,
            "unit_value": 420.0,
            "expiry_date": (reference_date - timedelta(days=10)).isoformat(),  # EXPIRED 10 DAYS AGO
            "avg_daily_demand": 1.5,
            "destination_location": "Clinic-A",
            "destination_daily_demand": 3.0,
            "transfer_distance_km": 58.0,
            "temperature_sensitive": True,
            "data_quality_score": 95.0,
            "expected_outcome": "BLOCKED / NO TRANSFER (Already expired)",
        },
        {
            # CASE 5: Destination demand lower than available quantity -> transfer capped to demand
            "batch_id": "EDGE-005",
            "medicine_code": "MED-D04",
            "medicine_name": "Adalimumab 40mg/0.8mL Pen",
            "medicine_category": "Immunology",
            "source_location": "Clinic-D",
            "quantity": 100.0,
            "unit_value": 310.0,
            "expiry_date": (reference_date + timedelta(days=15)).isoformat(),
            "avg_daily_demand": 1.0,  # 15 local consumption -> 85 surplus
            "destination_location": "Clinic-E",
            "destination_daily_demand": 2.0,  # 15 * 2.0 = 30 expected capacity
            "transfer_distance_km": 65.0,
            "temperature_sensitive": True,
            "data_quality_score": 98.0,
            "expected_outcome": "Transfer quantity capped to 30 units (destination capacity)",
        },
        {
            # CASE 6: Very long transfer distance -> low location score
            "batch_id": "EDGE-006",
            "medicine_code": "MED-F06",
            "medicine_name": "Infliximab Infusion 100mg",
            "medicine_category": "Immunology",
            "source_location": "Clinic-A",
            "quantity": 70.0,
            "unit_value": 295.0,
            "expiry_date": (reference_date + timedelta(days=18)).isoformat(),
            "avg_daily_demand": 0.5,
            "destination_location": "Clinic-E",
            "destination_daily_demand": 4.0,
            "transfer_distance_km": 290.0,  # VERY LONG DISTANCE
            "temperature_sensitive": True,
            "data_quality_score": 92.0,
            "expected_outcome": "Low location score and cold-chain risk penalty",
        },
        {
            # CASE 7: High expiry risk but no destination demand -> No transfer / local review
            "batch_id": "EDGE-007",
            "medicine_code": "MED-I09",
            "medicine_name": "Rituximab 500mg/50mL Concentrate",
            "medicine_category": "Oncology",
            "source_location": "Clinic-B",
            "quantity": 50.0,
            "unit_value": 450.0,
            "expiry_date": (reference_date + timedelta(days=12)).isoformat(),
            "avg_daily_demand": 0.5,
            "destination_location": "Clinic-C",
            "destination_daily_demand": 0.0,  # ZERO DESTINATION DEMAND
            "transfer_distance_km": 38.0,
            "temperature_sensitive": True,
            "data_quality_score": 94.0,
            "expected_outcome": "NO ACTION / Zero transfer quantity recommended",
        },
    ]


def generate_stakeholder_feedback() -> List[Dict[str, Any]]:
    """Synthetic stakeholder validation ratings and feedback (Likert 1-5)."""
    return [
        {
            "role": "Pharmacist",
            "question": "Is the recommendation understandable?",
            "score": 4.8,
            "feedback": "Rules for expiry urgency and local surplus calculations are clear and clinically sound.",
        },
        {
            "role": "Pharmacist",
            "question": "Is the explanation useful?",
            "score": 4.7,
            "feedback": "Having the exact formula and quantities broken down makes clinical review fast.",
        },
        {
            "role": "Inventory Manager",
            "question": "Is the workflow practical?",
            "score": 4.6,
            "feedback": "Limiting redistribution to destination demand capacity prevents creating second-hand waste.",
        },
        {
            "role": "Clinic Administrator",
            "question": "Is human approval appropriate?",
            "score": 4.9,
            "feedback": "Mandatory override reasons and audit logging satisfy hospital governance requirements.",
        },
        {
            "role": "Responsible AI Reviewer",
            "question": "Is uncertainty clear?",
            "score": 4.8,
            "feedback": "Visual confidence badges and explicit warnings for missing demand prevent automated over-trust.",
        },
        {
            "role": "Responsible AI Reviewer",
            "question": "Is human confirmation respected?",
            "score": 5.0,
            "feedback": "Rule 10 explicitly enforces human-in-the-loop decision-making. No unmonitored transfers.",
        },
    ]


def save_csv_files(base_data_dir: Path, inventory_records: List[Dict[str, Any]], edge_records: List[Dict[str, Any]], stakeholder_records: List[Dict[str, Any]]):
    """Save synthetic datasets to CSV files in the data/ directory."""
    import pandas as pd
    base_data_dir.mkdir(parents=True, exist_ok=True)

    # Save synthetic_inventory.csv
    df_inv = pd.DataFrame(inventory_records)
    today = date.today()
    df_inv["stock_value"] = df_inv["quantity"] * df_inv["unit_value"]
    df_inv["days_to_expiry"] = df_inv["expiry_date"].apply(
        lambda d: (datetime.strptime(str(d)[:10], "%Y-%m-%d").date() - today).days if d else -999
    )
    df_inv["potential_at_risk_value"] = df_inv.apply(
        lambda row: row["stock_value"] if row["days_to_expiry"] <= 45 else 0.0, axis=1
    )
    df_inv.to_csv(base_data_dir / "synthetic_inventory.csv", index=False)

    # Save edge_cases.csv
    df_edge = pd.DataFrame(edge_records)
    df_edge.to_csv(base_data_dir / "edge_cases.csv", index=False)

    # Save stakeholder_feedback.csv
    df_stakeholder = pd.DataFrame(stakeholder_records)
    df_stakeholder.to_csv(base_data_dir / "stakeholder_feedback.csv", index=False)


def populate_database(db, reference_date: date = None):
    """Seed the SQLite database with deterministic inventory, recommendations, and audit log."""
    if reference_date is None:
        reference_date = date.today()

    # Clear existing tables
    db.query(AuditLog).delete()
    db.query(Recommendation).delete()
    db.query(InventoryBatch).delete()
    db.commit()

    inventory_records = generate_synthetic_inventory(110, reference_date)
    edge_records = generate_edge_cases(reference_date)

    # Combine regular records with edge cases
    all_records = inventory_records + [
        {k: v for k, v in e.items() if k != "expected_outcome"} for e in edge_records
    ]

    # Save to data/ directory
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    stakeholder_records = generate_stakeholder_feedback()
    save_csv_files(data_dir, inventory_records, edge_records, stakeholder_records)

    # Insert Inventory batches
    for rec in all_records:
        batch = InventoryBatch(
            batch_id=rec["batch_id"],
            medicine_code=rec["medicine_code"],
            medicine_name=rec["medicine_name"],
            medicine_category=rec["medicine_category"],
            source_location=rec["source_location"],
            quantity=rec["quantity"],
            unit_value=rec["unit_value"],
            expiry_date=rec["expiry_date"],
            avg_daily_demand=rec["avg_daily_demand"],
            destination_location=rec["destination_location"],
            destination_daily_demand=rec["destination_daily_demand"],
            transfer_distance_km=rec["transfer_distance_km"],
            temperature_sensitive=rec["temperature_sensitive"],
            data_quality_score=rec["data_quality_score"],
        )
        db.add(batch)
    db.commit()

    # Generate Recommendations for each batch
    recommendations = []
    for rec in all_records:
        rec_data = evaluate_batch(rec, reference_date=reference_date)
        recommendation = Recommendation(
            recommendation_id=rec_data["recommendation_id"],
            batch_id=rec_data["batch_id"],
            medicine_code=rec_data["medicine_code"],
            medicine_name=rec_data["medicine_name"],
            source_location=rec_data["source_location"],
            destination_location=rec_data["destination_location"],
            current_quantity=rec_data["current_quantity"],
            recommended_transfer_quantity=rec_data["recommended_transfer_quantity"],
            days_to_expiry=rec_data["days_to_expiry"],
            stock_value=rec_data["stock_value"],
            risk_score=rec_data["risk_score"],
            expiry_score=rec_data["expiry_score"],
            surplus_score=rec_data["surplus_score"],
            demand_score=rec_data["demand_score"],
            location_score=rec_data["location_score"],
            data_quality_score=rec_data["data_quality_score"],
            priority=rec_data["priority"],
            confidence=rec_data["confidence"],
            confidence_level=rec_data["confidence_level"],
            status=rec_data["status"],
            explanation=rec_data["explanation"],
            evidence_json=json.dumps(rec_data["evidence"]),
        )
        db.add(recommendation)
        recommendations.append(recommendation)
    db.commit()

    # Seed 4 initial audit log entries for realistic initial experience
    # (1 Approved, 1 Overridden, 1 Rejected)
    initial_audits = [
        AuditLog(
            audit_id="AUD-001",
            recommendation_id="REC-BATCH-102",
            batch_id="BATCH-102",
            action="APPROVED",
            user_role="Pharmacist",
            reason="Verified surplus against oncology clinic schedule.",
            notes="Expedited courier scheduled for cold-chain transit at 09:00.",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3),
        ),
        AuditLog(
            audit_id="AUD-002",
            recommendation_id="REC-BATCH-105",
            batch_id="BATCH-105",
            action="OVERRIDDEN",
            user_role="Inventory Manager",
            reason="Stock already allocated",
            notes="15 units reserved for scheduled pediatric outpatient infusion.",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2),
        ),
        AuditLog(
            audit_id="AUD-003",
            recommendation_id="REC-BATCH-109",
            batch_id="BATCH-109",
            action="REJECTED",
            user_role="Clinic Administrator",
            reason="Transfer not feasible",
            notes="Transit vehicle refrigeration maintenance scheduled today.",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1),
        ),
    ]
    for aud in initial_audits:
        db.add(aud)

    # Update corresponding recommendation statuses to match audit trail
    rec_102 = db.query(Recommendation).filter_by(recommendation_id="REC-BATCH-102").first()
    if rec_102:
        rec_102.status = "APPROVED"

    rec_105 = db.query(Recommendation).filter_by(recommendation_id="REC-BATCH-105").first()
    if rec_105:
        rec_105.status = "OVERRIDDEN"

    rec_109 = db.query(Recommendation).filter_by(recommendation_id="REC-BATCH-109").first()
    if rec_109:
        rec_109.status = "REJECTED"

    db.commit()
