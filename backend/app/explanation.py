"""Explanation layer and evidence synthesis for ExpiryAware recommendations.

Generates human-readable clinical rationale, triggered rule summaries,
and transparent uncertainty breakdowns.
"""
from typing import Dict, Any, List


def generate_explanation(
    batch_id: str,
    medicine_code: str,
    medicine_name: str,
    source_location: str,
    destination_location: str,
    transfer_qty: float,
    current_qty: float,
    days_to_expiry: int,
    distance_km: float,
    confidence: float,
    confidence_reasons: List[str],
    rules_triggered: List[str],
    validation_status: str
) -> Dict[str, Any]:
    """Generate human-readable narrative and structured clinical evidence."""

    if validation_status == "BLOCKED":
        narrative = (
            f"Batch {batch_id} ({medicine_name}) redistribution is BLOCKED. "
            f"Safety or data integrity constraints prevent safe transfer."
        )
    elif transfer_qty <= 0:
        narrative = (
            f"Batch {batch_id} ({medicine_name}) is currently maintained at {source_location}. "
            f"Local projected consumption is sufficient to utilize stock before expiry ({days_to_expiry} days), "
            f"or candidate destination has insufficient demand. No transfer recommended."
        )
    else:
        dest_str = destination_location if destination_location else "eligible clinic"
        dist_str = f"{distance_km:.0f} km" if distance_km is not None else "measured distance"
        narrative = (
            f"Batch {batch_id} ({medicine_code} - {medicine_name}) is recommended for transfer "
            f"from {source_location} to {dest_str} ({transfer_qty:.0f} of {current_qty:.0f} units). "
            f"The batch expires in {days_to_expiry} days. {source_location} has surplus stock above local demand, "
            f"and {dest_str} exhibits active clinical consumption demand. Transfer distance is {dist_str}."
        )

    return {
        "narrative": narrative,
        "rules_triggered": rules_triggered,
        "confidence_reasons": confidence_reasons
    }
