"""FastAPI main application for ExpiryAware backend.

Provides RESTful endpoints for dashboard metrics, inventory management,
explainable recommendations, human approvals, audit logs, data quality, and evaluation.
"""
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, date, timezone
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models import InventoryBatch, Recommendation, AuditLog
from .schemas import (
    InventoryBatchResponse,
    RecommendationResponse,
    ActionRequest,
    OverrideRequest,
    AuditLogResponse,
    DashboardStats,
    DataQualityReport,
    FlaggedBatchInfo,
    EvaluationReport,
)
from .validation import validate_inventory_record
from .seed_data import populate_database
from .evaluation import run_evaluation_simulation

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("expiry_aware")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database is created and seeded on server launch."""
    logger.info("Initializing database...")
    init_db(seed_if_empty=True)
    logger.info("Database initialized successfully.")
    yield


app = FastAPI(
    title="ExpiryAware API",
    description="Responsible inventory intelligence and stock redistribution recommender for specialty medicines.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """System health check and database connectivity verification."""
    try:
        count = db.query(InventoryBatch).count()
        return {
            "status": "healthy",
            "service": "ExpiryAware Recommender",
            "version": "1.0.0",
            "database": "connected",
            "batch_count": count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error(f"Health check database failure: {exc}")
        return {
            "status": "degraded",
            "service": "ExpiryAware Recommender",
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ---------------------------------------------------------------------------
# Seed & Reset Demo Data
# ---------------------------------------------------------------------------
@app.post("/api/seed", tags=["System"])
def seed_demo_data(db: Session = Depends(get_db)):
    """Reset the application data to deterministic synthetic state for reproducible demo runs."""
    try:
        populate_database(db)
        logger.info("Database re-seeded with deterministic synthetic dataset.")
        return {
            "success": True,
            "message": "Demo data successfully reset to deterministic baseline.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to reset demo data: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset demo data: {str(exc)}"
        )


# ---------------------------------------------------------------------------
# Dashboard Endpoint
# ---------------------------------------------------------------------------
@app.get("/api/dashboard", response_model=DashboardStats, tags=["Dashboard"])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Aggregated company-level KPIs and chart distributions."""
    batches = db.query(InventoryBatch).all()
    recommendations = db.query(Recommendation).all()

    today = date.today()
    rec_by_batch = {r.batch_id: r for r in recommendations}

    total_batches = len(batches)
    near_expiry_batches = 0
    stock_at_risk_value = 0.0
    recommended_transfers_count = 0
    value_saved_protected = 0.0
    pending_approvals_count = 0

    location_map = {}
    expiry_buckets = {
        "Critical (<=15d)": {"count": 0, "value": 0.0},
        "Urgent (16-30d)": {"count": 0, "value": 0.0},
        "Mid-term (31-90d)": {"count": 0, "value": 0.0},
        "Safe (>90d)": {"count": 0, "value": 0.0},
    }
    priority_map = {
        "HIGH PRIORITY": {"count": 0, "value": 0.0},
        "MEDIUM PRIORITY": {"count": 0, "value": 0.0},
        "LOW PRIORITY": {"count": 0, "value": 0.0},
        "NO ACTION": {"count": 0, "value": 0.0},
    }

    for b in batches:
        rec = rec_by_batch.get(b.batch_id)
        days = rec.days_to_expiry if rec else 60
        qty = max(b.quantity, 0.0) if b.quantity is not None else 0.0
        unit_val = max(b.unit_value, 0.0) if b.unit_value is not None else 0.0
        val = qty * unit_val

        # Location breakdown
        loc = b.source_location or "Unknown"
        if loc not in location_map:
            location_map[loc] = {"batch_count": 0, "total_quantity": 0.0, "total_value": 0.0, "at_risk_value": 0.0}
        location_map[loc]["batch_count"] += 1
        location_map[loc]["total_quantity"] += qty
        location_map[loc]["total_value"] += val

        # Near expiry & at risk
        if 0 < days <= 30:
            near_expiry_batches += 1
            stock_at_risk_value += val
            location_map[loc]["at_risk_value"] += val

        # Expiry buckets
        if days <= 15:
            expiry_buckets["Critical (<=15d)"]["count"] += 1
            expiry_buckets["Critical (<=15d)"]["value"] += val
        elif days <= 30:
            expiry_buckets["Urgent (16-30d)"]["count"] += 1
            expiry_buckets["Urgent (16-30d)"]["value"] += val
        elif days <= 90:
            expiry_buckets["Mid-term (31-90d)"]["count"] += 1
            expiry_buckets["Mid-term (31-90d)"]["value"] += val
        else:
            expiry_buckets["Safe (>90d)"]["count"] += 1
            expiry_buckets["Safe (>90d)"]["value"] += val

    for r in recommendations:
        if r.status in ("PENDING", "WARNING") and r.recommended_transfer_quantity > 0:
            pending_approvals_count += 1

        if r.recommended_transfer_quantity > 0 and r.status != "BLOCKED":
            recommended_transfers_count += 1
            # Protected value calculation
            batch_obj = next((b for b in batches if b.batch_id == r.batch_id), None)
            unit_v = batch_obj.unit_value if batch_obj else (r.stock_value / max(r.current_quantity, 1.0))
            transfer_val = r.recommended_transfer_quantity * unit_v
            value_saved_protected += transfer_val

        # Priority distribution
        p = r.priority if r.priority in priority_map else "NO ACTION"
        priority_map[p]["count"] += 1
        batch_obj = next((b for b in batches if b.batch_id == r.batch_id), None)
        unit_v = batch_obj.unit_value if batch_obj else 0.0
        priority_map[p]["value"] += (r.recommended_transfer_quantity * unit_v)

    stock_by_location = [
        {
            "location": loc,
            "batch_count": data["batch_count"],
            "total_quantity": round(data["total_quantity"], 1),
            "total_value": round(data["total_value"], 2),
            "at_risk_value": round(data["at_risk_value"], 2),
        }
        for loc, data in sorted(location_map.items())
    ]

    near_expiry_breakdown = [
        {"range_label": label, "count": data["count"], "value": round(data["value"], 2)}
        for label, data in expiry_buckets.items()
    ]

    priority_distribution = [
        {"priority": p, "count": data["count"], "transfer_value": round(data["value"], 2)}
        for p, data in priority_map.items()
    ]

    # Quick evaluation summary for dashboard
    eval_sim = run_evaluation_simulation(db)

    return {
        "total_batches": total_batches,
        "near_expiry_batches": near_expiry_batches,
        "stock_at_risk_value": round(stock_at_risk_value, 2),
        "recommended_transfers_count": recommended_transfers_count,
        "value_saved_protected": round(value_saved_protected, 2),
        "pending_approvals_count": pending_approvals_count,
        "stock_by_location": stock_by_location,
        "near_expiry_breakdown": near_expiry_breakdown,
        "priority_distribution": priority_distribution,
        "baseline_vs_proposed_savings": {
            "waste_avoided_amount": eval_sim["waste_avoided_amount"],
            "waste_avoided_percentage": eval_sim["waste_avoided_percentage"],
            "baseline_waste": eval_sim["baseline_summary"]["stock_expired_waste"],
            "proposed_waste": eval_sim["proposed_summary"]["stock_expired_waste"]
        }
    }


# ---------------------------------------------------------------------------
# Inventory Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/inventory", response_model=List[InventoryBatchResponse], tags=["Inventory"])
def get_inventory(
    location: Optional[str] = Query(None, description="Filter by location (e.g. Clinic-A)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Oncology)"),
    search: Optional[str] = Query(None, description="Search batch ID, medicine code or name"),
    near_expiry_only: bool = Query(False, description="Filter <= 30 days to expiry"),
    temp_sensitive: Optional[bool] = Query(None, description="Filter temperature sensitive"),
    db: Session = Depends(get_db)
):
    """Retrieve inventory batches with filtering, search, and calculated clinical fields."""
    query = db.query(InventoryBatch)

    if location and location != "All":
        query = query.filter(InventoryBatch.source_location == location)
    if category and category != "All":
        query = query.filter(InventoryBatch.medicine_category == category)
    if temp_sensitive is not None:
        query = query.filter(InventoryBatch.temperature_sensitive == temp_sensitive)

    batches = query.all()
    results = []
    today = date.today()

    for b in batches:
        # Search query matching
        if search:
            s = search.lower()
            if (s not in b.batch_id.lower() and
                s not in b.medicine_code.lower() and
                s not in b.medicine_name.lower() and
                s not in b.source_location.lower()):
                continue

        qty = max(b.quantity, 0.0) if b.quantity is not None else 0.0
        unit_v = max(b.unit_value, 0.0) if b.unit_value is not None else 0.0
        stock_val = round(qty * unit_v, 2)

        try:
            exp_date = datetime.strptime(str(b.expiry_date)[:10], "%Y-%m-%d").date()
            days = (exp_date - today).days
        except Exception:
            days = -9999

        if near_expiry_only and (days > 30 or days <= 0):
            continue

        at_risk = stock_val if (0 < days <= 45) else 0.0

        val_status = "VALID"
        if b.data_quality_score < 75 or not b.destination_daily_demand:
            val_status = "WARNING"
        if days <= 0 or b.quantity <= 0 or not b.expiry_date:
            val_status = "BLOCKED"

        results.append(
            InventoryBatchResponse(
                batch_id=b.batch_id,
                medicine_code=b.medicine_code,
                medicine_name=b.medicine_name,
                medicine_category=b.medicine_category,
                source_location=b.source_location,
                quantity=b.quantity,
                unit_value=b.unit_value,
                expiry_date=b.expiry_date,
                avg_daily_demand=b.avg_daily_demand,
                destination_location=b.destination_location,
                destination_daily_demand=b.destination_daily_demand,
                transfer_distance_km=b.transfer_distance_km,
                temperature_sensitive=b.temperature_sensitive,
                data_quality_score=b.data_quality_score,
                stock_value=stock_val,
                days_to_expiry=days,
                potential_at_risk_value=at_risk,
                validation_status=val_status,
                created_at=b.created_at,
            )
        )

    return results


@app.get("/api/inventory/{batch_id}", response_model=InventoryBatchResponse, tags=["Inventory"])
def get_inventory_batch(batch_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a single inventory batch."""
    b = db.query(InventoryBatch).filter(InventoryBatch.batch_id == batch_id).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch '{batch_id}' not found.")

    today = date.today()
    qty = max(b.quantity, 0.0) if b.quantity is not None else 0.0
    unit_v = max(b.unit_value, 0.0) if b.unit_value is not None else 0.0
    stock_val = round(qty * unit_v, 2)
    try:
        exp_date = datetime.strptime(str(b.expiry_date)[:10], "%Y-%m-%d").date()
        days = (exp_date - today).days
    except Exception:
        days = -9999

    val_res = validate_inventory_record({
        "batch_id": b.batch_id,
        "medicine_code": b.medicine_code,
        "source_location": b.source_location,
        "quantity": b.quantity,
        "unit_value": b.unit_value,
        "expiry_date": b.expiry_date,
        "destination_daily_demand": b.destination_daily_demand,
        "transfer_distance_km": b.transfer_distance_km,
        "temperature_sensitive": b.temperature_sensitive,
    })

    return InventoryBatchResponse(
        batch_id=b.batch_id,
        medicine_code=b.medicine_code,
        medicine_name=b.medicine_name,
        medicine_category=b.medicine_category,
        source_location=b.source_location,
        quantity=b.quantity,
        unit_value=b.unit_value,
        expiry_date=b.expiry_date,
        avg_daily_demand=b.avg_daily_demand,
        destination_location=b.destination_location,
        destination_daily_demand=b.destination_daily_demand,
        transfer_distance_km=b.transfer_distance_km,
        temperature_sensitive=b.temperature_sensitive,
        data_quality_score=b.data_quality_score,
        stock_value=stock_val,
        days_to_expiry=days,
        potential_at_risk_value=stock_val if (0 < days <= 45) else 0.0,
        validation_status=val_res.status,
        created_at=b.created_at,
    )


# ---------------------------------------------------------------------------
# Recommendations Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/recommendations", response_model=List[RecommendationResponse], tags=["Recommendations"])
def get_recommendations(
    priority: Optional[str] = Query(None, description="Filter priority (HIGH PRIORITY, MEDIUM PRIORITY, etc.)"),
    status_filter: Optional[str] = Query(None, description="Filter status (PENDING, APPROVED, REJECTED, OVERRIDDEN, BLOCKED)"),
    db: Session = Depends(get_db)
):
    """Retrieve redistribution recommendations with full explainability and rule triggers."""
    query = db.query(Recommendation)

    if priority and priority != "All":
        query = query.filter(Recommendation.priority == priority)
    if status_filter and status_filter != "All":
        query = query.filter(Recommendation.status == status_filter)

    recs = query.order_by(Recommendation.risk_score.desc()).all()
    out = []
    for r in recs:
        evidence = {}
        try:
            evidence = json.loads(r.evidence_json)
        except Exception:
            pass

        out.append(
            RecommendationResponse(
                recommendation_id=r.recommendation_id,
                batch_id=r.batch_id,
                medicine_code=r.medicine_code,
                medicine_name=r.medicine_name,
                source_location=r.source_location,
                destination_location=r.destination_location,
                current_quantity=r.current_quantity,
                recommended_transfer_quantity=r.recommended_transfer_quantity,
                days_to_expiry=r.days_to_expiry,
                stock_value=r.stock_value,
                risk_score=r.risk_score,
                expiry_score=r.expiry_score,
                surplus_score=r.surplus_score,
                demand_score=r.demand_score,
                location_score=r.location_score,
                data_quality_score=r.data_quality_score,
                priority=r.priority,
                confidence=r.confidence,
                confidence_level=r.confidence_level,
                status=r.status,
                explanation=r.explanation,
                evidence=evidence,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return out


@app.get("/api/recommendations/{recommendation_id}", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a single recommendation."""
    r = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recommendation '{recommendation_id}' not found.")

    evidence = {}
    try:
        evidence = json.loads(r.evidence_json)
    except Exception:
        pass

    return RecommendationResponse(
        recommendation_id=r.recommendation_id,
        batch_id=r.batch_id,
        medicine_code=r.medicine_code,
        medicine_name=r.medicine_name,
        source_location=r.source_location,
        destination_location=r.destination_location,
        current_quantity=r.current_quantity,
        recommended_transfer_quantity=r.recommended_transfer_quantity,
        days_to_expiry=r.days_to_expiry,
        stock_value=r.stock_value,
        risk_score=r.risk_score,
        expiry_score=r.expiry_score,
        surplus_score=r.surplus_score,
        demand_score=r.demand_score,
        location_score=r.location_score,
        data_quality_score=r.data_quality_score,
        priority=r.priority,
        confidence=r.confidence,
        confidence_level=r.confidence_level,
        status=r.status,
        explanation=r.explanation,
        evidence=evidence,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


# ---------------------------------------------------------------------------
# Human-in-the-Loop Actions: Approve, Reject, Override
# ---------------------------------------------------------------------------
@app.post("/api/recommendations/{recommendation_id}/approve", tags=["Human Approval"])
def approve_recommendation(recommendation_id: str, req: ActionRequest, db: Session = Depends(get_db)):
    """Human approval of recommendation. Changes status to APPROVED and logs to audit trail."""
    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recommendation '{recommendation_id}' not found.")

    if rec.status == "BLOCKED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Blocked recommendations cannot be approved.")

    rec.status = "APPROVED"
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    rec.updated_at = now_utc

    # Create audit log entry
    audit_id = f"AUD-{now_utc.strftime('%Y%m%d%H%M%S')}-{rec.batch_id}"
    audit_entry = AuditLog(
        audit_id=audit_id,
        recommendation_id=rec.recommendation_id,
        batch_id=rec.batch_id,
        action="APPROVED",
        user_role=req.user_role,
        reason=req.reason or "Clinical confirmation verified.",
        notes=req.notes,
        timestamp=now_utc,
    )
    db.add(audit_entry)
    db.commit()

    logger.info(f"Recommendation {recommendation_id} APPROVED by {req.user_role}.")
    return {"success": True, "status": "APPROVED", "recommendation_id": recommendation_id, "audit_id": audit_id}


@app.post("/api/recommendations/{recommendation_id}/reject", tags=["Human Approval"])
def reject_recommendation(recommendation_id: str, req: ActionRequest, db: Session = Depends(get_db)):
    """Human rejection of recommendation. Changes status to REJECTED and logs to audit trail."""
    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recommendation '{recommendation_id}' not found.")

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    rec.status = "REJECTED"
    rec.updated_at = now_utc

    audit_id = f"AUD-{now_utc.strftime('%Y%m%d%H%M%S')}-{rec.batch_id}"
    audit_entry = AuditLog(
        audit_id=audit_id,
        recommendation_id=rec.recommendation_id,
        batch_id=rec.batch_id,
        action="REJECTED",
        user_role=req.user_role,
        reason=req.reason or "Clinical rejection.",
        notes=req.notes,
        timestamp=now_utc,
    )
    db.add(audit_entry)
    db.commit()

    logger.info(f"Recommendation {recommendation_id} REJECTED by {req.user_role}.")
    return {"success": True, "status": "REJECTED", "recommendation_id": recommendation_id, "audit_id": audit_id}


@app.post("/api/recommendations/{recommendation_id}/override", tags=["Human Approval"])
def override_recommendation(recommendation_id: str, req: OverrideRequest, db: Session = Depends(get_db)):
    """Human override with mandatory clinical reason capture.
    
    Allowed reasons:
    - Demand changed
    - Stock already allocated
    - Temperature concern
    - Transfer not feasible
    - Data appears incorrect
    - Other
    """
    allowed_reasons = [
        "Demand changed",
        "Stock already allocated",
        "Temperature concern",
        "Transfer not feasible",
        "Data appears incorrect",
        "Other"
    ]

    if not req.reason or req.reason.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Override reason cannot be empty. Mandatory reason code required for clinical governance."
        )

    if req.reason not in allowed_reasons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid override reason '{req.reason}'. Must be one of: {', '.join(allowed_reasons)}"
        )

    if not req.user_role or req.user_role.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff user role is required for override accountability."
        )

    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recommendation '{recommendation_id}' not found.")

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    rec.status = "OVERRIDDEN"
    rec.updated_at = now_utc

    audit_id = f"AUD-{now_utc.strftime('%Y%m%d%H%M%S')}-{rec.batch_id}"
    audit_entry = AuditLog(
        audit_id=audit_id,
        recommendation_id=rec.recommendation_id,
        batch_id=rec.batch_id,
        action="OVERRIDDEN",
        user_role=req.user_role,
        reason=req.reason,
        notes=req.notes,
        timestamp=now_utc,
    )
    db.add(audit_entry)
    db.commit()

    logger.info(f"Recommendation {recommendation_id} OVERRIDDEN by {req.user_role}. Reason: {req.reason}")
    return {"success": True, "status": "OVERRIDDEN", "recommendation_id": recommendation_id, "audit_id": audit_id}


# ---------------------------------------------------------------------------
# Audit Trail Endpoint
# ---------------------------------------------------------------------------
@app.get("/api/audit", response_model=List[AuditLogResponse], tags=["Audit Log"])
def get_audit_log(
    action: Optional[str] = Query(None, description="Filter by action: APPROVED, REJECTED, OVERRIDDEN"),
    db: Session = Depends(get_db)
):
    """Retrieve full immutable audit trail of clinical redistribution decisions."""
    query = db.query(AuditLog)
    if action and action != "All":
        query = query.filter(AuditLog.action == action)
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    return logs


# ---------------------------------------------------------------------------
# Data Quality Endpoint
# ---------------------------------------------------------------------------
@app.get("/api/data-quality", response_model=DataQualityReport, tags=["Data Quality"])
def get_data_quality_report(db: Session = Depends(get_db)):
    """Examine inventory data integrity and surface actionable validation warnings."""
    batches = db.query(InventoryBatch).all()
    total = len(batches)

    missing_expiry = 0
    missing_demand = 0
    invalid_qty = 0
    invalid_dates = 0
    low_quality = 0
    complete_records = 0
    flagged: List[FlaggedBatchInfo] = []

    sum_dq = 0.0

    for b in batches:
        sum_dq += b.data_quality_score
        val = validate_inventory_record({
            "batch_id": b.batch_id,
            "medicine_code": b.medicine_code,
            "source_location": b.source_location,
            "quantity": b.quantity,
            "unit_value": b.unit_value,
            "expiry_date": b.expiry_date,
            "destination_daily_demand": b.destination_daily_demand,
            "transfer_distance_km": b.transfer_distance_km,
            "temperature_sensitive": b.temperature_sensitive,
        })

        is_flagged = False
        if val.flags.get("missing_expiry_date"):
            missing_expiry += 1
            is_flagged = True
        if val.flags.get("invalid_expiry_date") or val.flags.get("already_expired"):
            invalid_dates += 1
            is_flagged = True
        if val.flags.get("negative_quantity") or val.flags.get("zero_quantity") or val.flags.get("missing_quantity"):
            invalid_qty += 1
            is_flagged = True
        if val.flags.get("missing_destination_demand"):
            missing_demand += 1
            is_flagged = True
        if b.data_quality_score < 75.0:
            low_quality += 1
            is_flagged = True

        if val.status == "VALID" and b.data_quality_score >= 85.0:
            complete_records += 1

        if is_flagged:
            flagged.append(
                FlaggedBatchInfo(
                    batch_id=b.batch_id,
                    medicine_code=b.medicine_code,
                    source_location=b.source_location,
                    issue=val.explanation,
                    severity=val.status,
                    data_quality_score=b.data_quality_score,
                )
            )

    overall_score = round(sum_dq / total, 1) if total > 0 else 100.0

    return DataQualityReport(
        total_records=total,
        complete_records=complete_records,
        missing_expiry_count=missing_expiry,
        missing_demand_count=missing_demand,
        invalid_quantity_count=invalid_qty,
        invalid_dates_count=invalid_dates,
        low_quality_count=low_quality,
        overall_quality_score=overall_score,
        flagged_batches=flagged,
    )


# ---------------------------------------------------------------------------
# Evaluation Endpoint
# ---------------------------------------------------------------------------
@app.get("/api/evaluation", response_model=EvaluationReport, tags=["Evaluation"])
def get_evaluation_report(db: Session = Depends(get_db)):
    """Run measurable simulation comparing baseline FIFO against proposed ExpiryAware system."""
    eval_data = run_evaluation_simulation(db)
    return eval_data
