"""Robust data validation module for ExpiryAware inventory records.

Checks for missing, invalid, or suspicious fields and classifies records as:
- VALID: Clean data, ready for optimal recommendation.
- WARNING: Minor or missing optional fields (e.g. demand), confidence reduced.
- BLOCKED: Critical data missing or corrupt; redistribution strictly prohibited.
"""
from datetime import datetime, date
from typing import Dict, Any, List
from .schemas import ValidationResult


def validate_inventory_record(record: Dict[str, Any], reference_date: date = None) -> ValidationResult:
    """Validate a single inventory batch record against clinical data integrity rules."""
    if reference_date is None:
        reference_date = date.today()

    reasons: List[str] = []
    flags: Dict[str, Any] = {}
    is_blocked = False
    has_warning = False

    # 1. Batch ID check
    batch_id = record.get("batch_id")
    if not batch_id or str(batch_id).strip() == "":
        is_blocked = True
        reasons.append("Batch ID is missing. Record cannot be tracked.")
        flags["missing_batch_id"] = True

    # 2. Medicine code check
    med_code = record.get("medicine_code")
    if not med_code or str(med_code).strip() == "":
        is_blocked = True
        reasons.append("Medicine code is missing. Item identification impossible.")
        flags["missing_medicine_code"] = True

    # 3. Source location check
    source_loc = record.get("source_location")
    if not source_loc or str(source_loc).strip() == "":
        is_blocked = True
        reasons.append("Source location is unavailable. Origin must be known.")
        flags["missing_source_location"] = True

    # 4. Expiry date check
    expiry_raw = record.get("expiry_date")
    parsed_expiry = None
    if not expiry_raw or str(expiry_raw).strip() == "" or str(expiry_raw).lower() in ("nan", "none", "null"):
        is_blocked = True
        reasons.append("Expiry date is unavailable. Redistribution cannot be safely prioritised.")
        flags["missing_expiry_date"] = True
    else:
        try:
            parsed_expiry = datetime.strptime(str(expiry_raw).strip()[:10], "%Y-%m-%d").date()
            days_to_expiry = (parsed_expiry - reference_date).days
            flags["days_to_expiry"] = days_to_expiry

            if days_to_expiry <= 0:
                is_blocked = True
                reasons.append(f"Batch is already expired ({days_to_expiry} days past expiry). Redistribution strictly prohibited.")
                flags["already_expired"] = True
        except (ValueError, TypeError):
            is_blocked = True
            reasons.append(f"Invalid expiry date format ('{expiry_raw}'). Expected YYYY-MM-DD.")
            flags["invalid_expiry_date"] = True

    # 5. Quantity checks
    qty = record.get("quantity")
    if qty is None or str(qty).lower() in ("nan", "none", "null"):
        is_blocked = True
        reasons.append("Quantity is missing.")
        flags["missing_quantity"] = True
    else:
        try:
            qty_float = float(qty)
            if qty_float < 0:
                is_blocked = True
                reasons.append(f"Quantity is invalid ({qty_float}). Stock cannot be negative.")
                flags["negative_quantity"] = True
            elif qty_float == 0:
                is_blocked = True
                reasons.append("Quantity is zero. No stock available for redistribution.")
                flags["zero_quantity"] = True
        except (ValueError, TypeError):
            is_blocked = True
            reasons.append(f"Quantity is non-numeric: '{qty}'.")
            flags["invalid_quantity"] = True

    # 6. Unit value checks
    unit_val = record.get("unit_value")
    if unit_val is None or str(unit_val).lower() in ("nan", "none", "null"):
        has_warning = True
        reasons.append("Unit value is missing; estimated as default baseline.")
        flags["missing_unit_value"] = True
    else:
        try:
            unit_float = float(unit_val)
            if unit_float < 0:
                is_blocked = True
                reasons.append(f"Unit value is negative ({unit_float}). Financial calculations compromised.")
                flags["negative_unit_value"] = True
        except (ValueError, TypeError):
            has_warning = True
            reasons.append(f"Unit value is non-numeric: '{unit_val}'.")
            flags["invalid_unit_value"] = True

    # 7. Demand checks
    dest_demand = record.get("destination_daily_demand")
    if dest_demand is None or str(dest_demand).lower() in ("nan", "none", "null"):
        has_warning = True
        reasons.append("Destination demand is unavailable. Recommendation confidence is reduced.")
        flags["missing_destination_demand"] = True
    else:
        try:
            dest_demand_float = float(dest_demand)
            if dest_demand_float < 0:
                has_warning = True
                reasons.append(f"Destination demand is negative ({dest_demand_float}). Defaulting to 0.")
                flags["negative_destination_demand"] = True
        except (ValueError, TypeError):
            has_warning = True
            reasons.append("Destination demand is non-numeric.")
            flags["invalid_destination_demand"] = True

    src_demand = record.get("avg_daily_demand")
    if src_demand is not None and str(src_demand).lower() not in ("nan", "none", "null"):
        try:
            src_demand_float = float(src_demand)
            if src_demand_float < 0:
                has_warning = True
                reasons.append("Source daily demand is negative. Defaulting to 0.")
                flags["negative_source_demand"] = True
        except (ValueError, TypeError):
            pass

    # 8. Transfer distance checks
    dist = record.get("transfer_distance_km")
    if dist is not None and str(dist).lower() not in ("nan", "none", "null"):
        try:
            dist_float = float(dist)
            if dist_float < 0:
                has_warning = True
                reasons.append(f"Transfer distance is negative ({dist_float} km).")
                flags["negative_distance"] = True
        except (ValueError, TypeError):
            has_warning = True
            reasons.append("Transfer distance is non-numeric.")
            flags["invalid_distance"] = True

    # 9. Temperature sensitivity check
    temp_sens = record.get("temperature_sensitive")
    if temp_sens is None or str(temp_sens).lower() in ("nan", "none", "null"):
        has_warning = True
        reasons.append("Temperature sensitivity flag is missing; assuming cold-chain required for safety.")
        flags["missing_temp_flag"] = True

    # Determine status and composite explanation
    if is_blocked:
        status = "BLOCKED"
        explanation = " | ".join(reasons)
    elif has_warning:
        status = "WARNING"
        explanation = " | ".join(reasons)
    else:
        status = "VALID"
        explanation = "All clinical data fields validated successfully."

    return ValidationResult(
        status=status,
        explanation=explanation,
        reasons=reasons,
        flags=flags
    )
