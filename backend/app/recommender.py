"""Explainable, rule-based recommendation engine for ExpiryAware.

Implements Rules 1-10 with transparent multi-factor scoring:
risk_score = 0.35 * expiry + 0.25 * surplus + 0.25 * demand + 0.10 * location + 0.05 * data_quality
"""
import json
import math
from datetime import date, datetime
from typing import Dict, Any, List, Tuple
from .validation import validate_inventory_record
from .explanation import generate_explanation


def compute_days_to_expiry(expiry_str: str, reference_date: date = None) -> int:
    """Compute days remaining until expiry date.

    Why this logic exists:
    A batch's shelf-life countdown dictates urgency. If the date string is malformed
    or missing, returning -9999 acts as an explicit sentinel that triggers safety blocks.
    """
    if reference_date is None:
        reference_date = date.today()
    try:
        exp = datetime.strptime(str(expiry_str).strip()[:10], "%Y-%m-%d").date()
        return (exp - reference_date).days
    except Exception:
        return -9999


def score_expiry(days_to_expiry: int) -> Tuple[float, str]:
    """Score urgency based on days to expiry (Weight: 35%).

    Why this logic exists:
    Specialty medicines within 30 days of expiry face immediate discard unless routed
    to higher-volume clinics. The scoring tiered curve applies a steep acceleration
    (88-100 pts) for batches <= 30 days, prioritizing them over stable (>90d) stock.
    Already-expired medicines (<=0d) receive 0.0 to prevent illegal redistribution.
    """
    if days_to_expiry <= 0:
        return 0.0, "EXPIRED"
    elif days_to_expiry <= 15:
        return 100.0, "CRITICAL"
    elif days_to_expiry <= 30:
        # RULE 1: If days_to_expiry <= 30: increase expiry urgency
        return 88.0, "HIGH"
    elif days_to_expiry <= 60:
        return 62.0, "MEDIUM"
    elif days_to_expiry <= 90:
        return 35.0, "LOW"
    else:
        return 10.0, "MINIMAL"


def score_surplus(quantity: float, days_to_expiry: int, avg_daily_demand: float) -> Tuple[float, float, bool]:
    """Score source clinic surplus based on local expected demand until expiry (Weight: 25%).

    Why this logic exists:
    Redistribution must NEVER create an artificial shortage at the source clinic.
    Projected local consumption = days_to_expiry * avg_daily_demand.
    Only stock in excess of local patient needs is classified as surplus. If local
    demand will consume the entire batch before expiry, surplus is 0 and transfer is unnecessary.
    Returns: (surplus_score, surplus_quantity, is_surplus)
    """
    if days_to_expiry <= 0 or quantity <= 0:
        return 0.0, 0.0, False

    daily_dem = avg_daily_demand if (avg_daily_demand is not None and avg_daily_demand >= 0) else 1.0
    expected_local_consumption = days_to_expiry * daily_dem
    surplus_qty = max(quantity - expected_local_consumption, 0.0)

    # RULE 2: If source quantity > expected source demand: mark source as surplus
    is_surplus = surplus_qty > 0

    if is_surplus:
        surplus_ratio = min(surplus_qty / max(quantity, 1.0), 1.0)
        score = 45.0 + (55.0 * surplus_ratio)
    else:
        # Stock will be consumed locally
        score = 15.0

    return min(score, 100.0), round(surplus_qty, 1), is_surplus


def score_demand(days_to_expiry: int, dest_demand: float, surplus_qty: float) -> Tuple[float, float, str]:
    """Score candidate destination clinic demand (Weight: 25%).

    Why this logic exists:
    A transfer recommendation is clinically useless unless the recipient clinic
    has verified ongoing patient treatments requiring the formulation.
    Expected destination capacity = days_to_expiry * dest_demand.
    If destination demand is zero or negative, the clinic is marked ineligible.
    If demand data is unavailable (None), a baseline fallback score (35.0) is
    used while triggering Rule 7 uncertainty warnings in downstream logic.
    Returns: (demand_score, expected_dest_capacity, demand_level)
    """
    if dest_demand is None:
        return 35.0, 0.0, "UNAVAILABLE"

    if dest_demand <= 0:
        return 0.0, 0.0, "NONE"

    # RULE 3: If destination demand > 0: destination is eligible
    expected_dest_capacity = max(days_to_expiry, 0) * dest_demand

    if expected_dest_capacity <= 0:
        return 0.0, 0.0, "NONE"

    if surplus_qty <= 0:
        return 50.0, round(expected_dest_capacity, 1), "MODERATE"

    demand_coverage_ratio = min(expected_dest_capacity / max(surplus_qty, 1.0), 1.5)
    score = min(demand_coverage_ratio * 70.0, 100.0)

    level = "HIGH" if score >= 75 else ("MEDIUM" if score >= 45 else "LOW")
    return round(score, 1), round(expected_dest_capacity, 1), level


def score_location(distance_km: float, temperature_sensitive: bool) -> Tuple[float, str]:
    """Score transfer logistics feasibility based on distance and cold chain requirements (Weight: 10%).

    Why this logic exists:
    Transferring biologics across long highway routes introduces cold-chain vulnerability
    and elevated transport costs. Distance is discretized into feasibility tiers:
      - <= 30 km:  100 pts (EXCELLENT local intradistrict transit)
      - <= 100 km:  85 pts (HIGH regional transit, Rule 4)
      - <= 180 km:  55 pts (MODERATE intercity transit)
      - <= 250 km:  30 pts (CHALLENGING long haul)
      - > 250 km:   15 pts (POOR logistics feasibility)
    For cold-chain biologics (2°C - 8°C), an extra 20-point penalty is assessed if
    transit exceeds 100 km to reflect thermal container hold-time limits.
    """
    if distance_km is None or distance_km < 0:
        return 50.0, "UNKNOWN"

    # RULE 4: If transfer distance <= 100 km: location feasibility is high
    if distance_km <= 30:
        base_score = 100.0
        label = "EXCELLENT"
    elif distance_km <= 100:
        base_score = 85.0
        label = "HIGH"
    elif distance_km <= 180:
        base_score = 55.0
        label = "MODERATE"
    elif distance_km <= 250:
        base_score = 30.0
        label = "CHALLENGING"
    else:
        base_score = 15.0
        label = "POOR"

    # Cold chain penalty for long transit
    if temperature_sensitive and distance_km > 100:
        base_score = max(base_score - 20.0, 10.0)
        label += " (Cold Chain Risk)"

    return base_score, label


def evaluate_batch(record: Dict[str, Any], reference_date: date = None) -> Dict[str, Any]:
    """Evaluate an inventory batch and generate complete explainable recommendation."""
    if reference_date is None:
        reference_date = date.today()

    val_result = validate_inventory_record(record, reference_date=reference_date)
    batch_id = record.get("batch_id", "UNKNOWN")
    med_code = record.get("medicine_code", "UNKNOWN")
    med_name = record.get("medicine_name", record.get("medicine_code", "Medicine"))
    source_loc = record.get("source_location", "Unknown Clinic")
    dest_loc = record.get("destination_location", "Clinic-B")
    qty = float(record.get("quantity") or 0.0)
    unit_val = float(record.get("unit_value") or 0.0)
    stock_value = round(qty * unit_val, 2)
    distance_km = float(record.get("transfer_distance_km")) if record.get("transfer_distance_km") is not None else 50.0
    temp_sensitive = bool(record.get("temperature_sensitive", False))
    data_quality = float(record.get("data_quality_score") or 100.0)
    days_to_expiry = compute_days_to_expiry(record.get("expiry_date", ""), reference_date)

    rules_triggered: List[str] = []
    confidence_reasons: List[str] = []

    # Check hard blocks:
    # RULE 5: If expiry date is missing: BLOCK recommendation
    # RULE 6: If quantity <= 0: BLOCK recommendation
    # RULE 9: Never recommend an expired batch
    if val_result.status == "BLOCKED":
        rules_triggered.append(f"SAFETY BLOCK: {val_result.explanation}")
        if val_result.flags.get("missing_expiry_date"):
            rules_triggered.append("RULE 5: Expiry date is unavailable. Redistribution blocked.")
        if val_result.flags.get("negative_quantity") or val_result.flags.get("zero_quantity"):
            rules_triggered.append("RULE 6: Quantity is invalid or zero. Redistribution blocked.")
        if val_result.flags.get("already_expired"):
            rules_triggered.append("RULE 9: Batch is already expired. Expired medicine cannot be transferred.")

        evidence = {
            "expiry_urgency": "EXPIRED" if days_to_expiry <= 0 else "UNAVAILABLE",
            "source_surplus": "BLOCKED",
            "destination_demand": "BLOCKED",
            "distance_feasibility": "BLOCKED",
            "temperature_control": "Cold Chain (2-8°C)" if temp_sensitive else "Ambient (15-25°C)",
            "data_quality": f"{data_quality:.0f}%",
            "validation_status": "BLOCKED"
        }

        explanation_data = generate_explanation(
            batch_id=batch_id,
            medicine_code=med_code,
            medicine_name=med_name,
            source_location=source_loc,
            destination_location=dest_loc,
            transfer_qty=0.0,
            current_qty=qty,
            days_to_expiry=days_to_expiry,
            distance_km=distance_km,
            confidence=0.0,
            confidence_reasons=["Data validation blocked"],
            rules_triggered=rules_triggered,
            validation_status="BLOCKED"
        )

        return {
            "recommendation_id": f"REC-{batch_id}",
            "batch_id": batch_id,
            "medicine_code": med_code,
            "medicine_name": med_name,
            "source_location": source_loc,
            "destination_location": dest_loc,
            "current_quantity": qty,
            "recommended_transfer_quantity": 0.0,
            "days_to_expiry": days_to_expiry,
            "stock_value": stock_value,
            "risk_score": 0.0,
            "expiry_score": 0.0,
            "surplus_score": 0.0,
            "demand_score": 0.0,
            "location_score": 0.0,
            "data_quality_score": data_quality,
            "priority": "NO ACTION",
            "confidence": 0.0,
            "confidence_level": "BLOCKED",
            "status": "BLOCKED",
            "explanation": explanation_data["narrative"],
            "evidence": evidence,
            "rules_triggered": rules_triggered
        }

    # Factor 1: Expiry score
    exp_score, exp_urgency = score_expiry(days_to_expiry)
    if days_to_expiry <= 30:
        rules_triggered.append(f"RULE 1: Days to expiry ({days_to_expiry} days) <= 30. High urgency applied.")

    # Factor 2: Surplus score
    src_demand = record.get("avg_daily_demand")
    surplus_score_val, surplus_qty, is_surplus = score_surplus(qty, days_to_expiry, src_demand)
    if is_surplus:
        rules_triggered.append(f"RULE 2: Source quantity ({qty:.0f}) exceeds projected consumption; surplus identified ({surplus_qty:.0f} units).")
    else:
        rules_triggered.append(f"RULE 2: Local projected consumption absorbs batch. Surplus is 0.")

    # Factor 3: Demand score
    dest_demand = record.get("destination_daily_demand")
    if dest_demand is None:
        # RULE 7: If important demand data is missing: reduce confidence and show WARNING
        rules_triggered.append("RULE 7: Destination demand data is missing. Confidence reduced, WARNING flag set.")
        confidence_reasons.append("Destination demand data is unavailable.")
    elif dest_demand > 0:
        # RULE 3: If destination demand > 0: destination is eligible
        rules_triggered.append(f"RULE 3: Destination {dest_loc} demand is active ({dest_demand:.1f}/day); eligible candidate.")

    dem_score_val, dest_capacity, dem_level = score_demand(days_to_expiry, dest_demand, surplus_qty)

    # Factor 4: Location score
    loc_score_val, loc_label = score_location(distance_km, temp_sensitive)
    if distance_km <= 100:
        rules_triggered.append(f"RULE 4: Transit distance ({distance_km:.0f} km) <= 100 km; high logistics feasibility.")
    else:
        rules_triggered.append(f"Logistics notice: Transit distance ({distance_km:.0f} km) exceeds 100 km.")

    # Factor 5: Data quality score (Weight: 5%)
    # Rewards records with complete attributes, clean date formats, and verified ledger tracking.
    dq_score_val = max(min(data_quality, 100.0), 0.0)

    # Multi-Factor Explainable Scoring Formula:
    # ------------------------------------------
    # Weights sum to 100% and balance clinical urgency against operational feasibility:
    #   - 35% Expiry Urgency: Primary clinical priority — preventing imminent drug expiry.
    #   - 25% Source Surplus: Ensures origin clinic has authentic excess beyond its own patient needs.
    #   - 25% Destination Demand: Ensures recipient facility has genuine capacity to consume before expiry.
    #   - 10% Location Logistics: Favors local/regional transfers and protects cold-chain viability.
    #   -  5% Data Quality: Penalizes incomplete ledger entries to discourage decision-making on dirty data.
    overall_risk_score = (
        0.35 * exp_score +
        0.25 * surplus_score_val +
        0.25 * dem_score_val +
        0.10 * loc_score_val +
        0.05 * dq_score_val
    )
    overall_risk_score = round(max(min(overall_risk_score, 100.0), 0.0), 1)

    # Transfer Quantity Calculation & Rule 8 Capping:
    # -----------------------------------------------
    # RULE 8: Never recommend transferring more than destination demand requires.
    # Formula: Transfer Qty = min(Surplus Qty, Destination Capacity, Total Available Stock)
    # Why this logic exists:
    # Transferring excess units beyond what the destination clinic can administer would
    # merely shift the expiration event from one clinic to another ("secondary waste").
    if surplus_qty > 0 and dest_capacity > 0:
        recommended_transfer_qty = min(surplus_qty, dest_capacity, qty)
        rules_triggered.append(
            f"RULE 8: Transfer quantity capped to {recommended_transfer_qty:.0f} units "
            f"(min of surplus {surplus_qty:.0f}, destination demand capacity {dest_capacity:.0f}, total stock {qty:.0f})."
        )
    else:
        recommended_transfer_qty = 0.0
        if surplus_qty <= 0:
            rules_triggered.append("Transfer quantity zero: No surplus stock after accounting for source local demand.")
        elif dest_capacity <= 0:
            rules_triggered.append("Transfer quantity zero: Destination clinic has no projected demand capacity.")

    # Determine Priority Band:
    # ------------------------
    # Stratifies recommendations for clinical dispensary workflows:
    #   - 80-100: HIGH PRIORITY   -> Immediate pharmacist review required (near-term expiry + high demand).
    #   - 60-79:  MEDIUM PRIORITY -> Active candidate for scheduled weekly inter-facility transfers.
    #   - 40-59:  LOW PRIORITY    -> Monitor local consumption; defer transfer unless demand shifts.
    #   - Below 40: NO ACTION     -> Surplus absorbed locally or recipient capacity absent.
    if recommended_transfer_qty <= 0:
        priority = "NO ACTION"
    elif overall_risk_score >= 80.0:
        priority = "HIGH PRIORITY"
    elif overall_risk_score >= 60.0:
        priority = "MEDIUM PRIORITY"
    elif overall_risk_score >= 40.0:
        priority = "LOW PRIORITY"
    else:
        priority = "NO ACTION"

    # Uncertainty & Confidence Calibration:
    # -------------------------------------
    # Base confidence mirrors data quality score, but degrades deterministically
    # when risk factors compound:
    #   - Missing destination demand: -25 pts (clinical destination uncertainty).
    #   - Cold-chain transit > 100 km: -15 pts (thermal container duration risk).
    #   - Short delivery window <= 7 days: -10 pts (tight courier margin for error).
    conf = dq_score_val
    if dest_demand is None:
        conf -= 25.0
    if temp_sensitive and distance_km > 100:
        conf -= 15.0
        confidence_reasons.append("Temperature-sensitive medicine requires cold-chain transport over >100 km.")
    if days_to_expiry <= 7 and days_to_expiry > 0:
        conf -= 10.0
        confidence_reasons.append(f"Short delivery window ({days_to_expiry} days remaining).")

    confidence = round(max(min(conf, 100.0), 15.0), 1)
    if confidence >= 90.0:
        conf_level = "HIGH CONFIDENCE"
    elif confidence >= 70.0:
        conf_level = "MEDIUM CONFIDENCE"
    else:
        conf_level = "LOW CONFIDENCE"

    # Status Assignment & Rule 10 Governance Mandate:
    # ------------------------------------------------
    # RULE 10: Never automatically approve a transfer.
    # The system is strictly decision-support (assistive, not autonomous).
    # Transfers require authorized human sign-off (Approve, Reject, or Override).
    rules_triggered.append("RULE 10: Transfer requires human clinical approval. System cannot execute autonomously.")
    if val_result.status == "WARNING":
        rec_status = "WARNING"
    elif recommended_transfer_qty > 0:
        rec_status = "PENDING"
    else:
        rec_status = "NO_ACTION"

    evidence = {
        "expiry_urgency": f"{exp_urgency} ({days_to_expiry}d)",
        "source_surplus": f"YES (+{surplus_qty:.0f} units)" if is_surplus else "NO (Local use)",
        "destination_demand": f"{dem_level} ({dest_capacity:.0f} cap)",
        "distance_feasibility": f"{loc_label} ({distance_km:.0f} km)",
        "temperature_control": "Cold Chain (2-8°C)" if temp_sensitive else "Ambient (15-25°C)",
        "data_quality": f"{data_quality:.0f}%",
        "validation_status": val_result.status
    }

    explanation_data = generate_explanation(
        batch_id=batch_id,
        medicine_code=med_code,
        medicine_name=med_name,
        source_location=source_loc,
        destination_location=dest_loc,
        transfer_qty=recommended_transfer_qty,
        current_qty=qty,
        days_to_expiry=days_to_expiry,
        distance_km=distance_km,
        confidence=confidence,
        confidence_reasons=confidence_reasons,
        rules_triggered=rules_triggered,
        validation_status=val_result.status
    )

    return {
        "recommendation_id": f"REC-{batch_id}",
        "batch_id": batch_id,
        "medicine_code": med_code,
        "medicine_name": med_name,
        "source_location": source_loc,
        "destination_location": dest_loc,
        "current_quantity": qty,
        "recommended_transfer_quantity": recommended_transfer_qty,
        "days_to_expiry": days_to_expiry,
        "stock_value": stock_value,
        "risk_score": overall_risk_score,
        "expiry_score": exp_score,
        "surplus_score": surplus_score_val,
        "demand_score": dem_score_val,
        "location_score": loc_score_val,
        "data_quality_score": dq_score_val,
        "priority": priority,
        "confidence": confidence,
        "confidence_level": conf_level,
        "status": rec_status,
        "explanation": explanation_data["narrative"],
        "evidence": evidence,
        "rules_triggered": rules_triggered
    }
