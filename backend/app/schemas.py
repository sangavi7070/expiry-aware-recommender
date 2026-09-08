"""Pydantic schemas for request validation and API responses."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# --- Inventory Schemas ---
class InventoryBatchBase(BaseModel):
    batch_id: str
    medicine_code: str
    medicine_name: str
    medicine_category: str
    source_location: str
    quantity: float
    unit_value: float
    expiry_date: str
    avg_daily_demand: Optional[float] = None
    destination_location: Optional[str] = None
    destination_daily_demand: Optional[float] = None
    transfer_distance_km: Optional[float] = None
    temperature_sensitive: bool = False
    data_quality_score: float = 100.0


class InventoryBatchResponse(InventoryBatchBase):
    stock_value: float
    days_to_expiry: int
    potential_at_risk_value: float
    validation_status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Validation Schemas ---
class ValidationResult(BaseModel):
    status: str  # VALID, WARNING, BLOCKED
    explanation: str
    reasons: List[str] = []
    flags: Dict[str, Any] = {}


# --- Recommendation Schemas ---
class RecommendationResponse(BaseModel):
    recommendation_id: str
    batch_id: str
    medicine_code: str
    medicine_name: str
    source_location: str
    destination_location: str
    current_quantity: float
    recommended_transfer_quantity: float
    days_to_expiry: int
    stock_value: float
    risk_score: float
    expiry_score: float
    surplus_score: float
    demand_score: float
    location_score: float
    data_quality_score: float
    priority: str  # HIGH PRIORITY, MEDIUM PRIORITY, LOW PRIORITY, NO ACTION
    confidence: float
    confidence_level: str  # HIGH CONFIDENCE, MEDIUM CONFIDENCE, LOW CONFIDENCE
    status: str  # PENDING, APPROVED, REJECTED, OVERRIDDEN, BLOCKED, WARNING
    explanation: str
    evidence: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Human Action Schemas ---
class ActionRequest(BaseModel):
    user_role: str = Field(default="Pharmacist", description="Staff role approving/rejecting")
    reason: Optional[str] = Field(default="Clinical review confirmed", description="Reason for action")
    notes: Optional[str] = Field(default=None, description="Optional staff notes")


class OverrideRequest(BaseModel):
    user_role: str = Field(..., description="Staff role (Pharmacist, Inventory Manager, Clinic Administrator, Clinical Lead)")
    reason: str = Field(..., description="Mandatory reason: 'Demand changed', 'Stock already allocated', 'Temperature concern', 'Transfer not feasible', 'Data appears incorrect', 'Other'")
    notes: Optional[str] = Field(default="", description="Detailed clinical notes")


# --- Audit Schemas ---
class AuditLogResponse(BaseModel):
    audit_id: str
    recommendation_id: str
    batch_id: Optional[str] = None
    action: str  # APPROVED, REJECTED, OVERRIDDEN
    user_role: str
    reason: str
    notes: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Schemas ---
class LocationStock(BaseModel):
    location: str
    batch_count: int
    total_quantity: float
    total_value: float
    at_risk_value: float


class ExpiryBreakdown(BaseModel):
    range_label: str
    count: int
    value: float


class PriorityDistribution(BaseModel):
    priority: str
    count: int
    transfer_value: float


class DashboardStats(BaseModel):
    total_batches: int
    near_expiry_batches: int
    stock_at_risk_value: float
    recommended_transfers_count: int
    value_saved_protected: float
    pending_approvals_count: int
    stock_by_location: List[LocationStock]
    near_expiry_breakdown: List[ExpiryBreakdown]
    priority_distribution: List[PriorityDistribution]
    baseline_vs_proposed_savings: Dict[str, Any]


# --- Data Quality Schemas ---
class FlaggedBatchInfo(BaseModel):
    batch_id: str
    medicine_code: str
    source_location: str
    issue: str
    severity: str  # BLOCKED, WARNING
    data_quality_score: float


class DataQualityReport(BaseModel):
    total_records: int
    complete_records: int
    missing_expiry_count: int
    missing_demand_count: int
    invalid_quantity_count: int
    invalid_dates_count: int
    low_quality_count: int
    overall_quality_score: float
    flagged_batches: List[FlaggedBatchInfo]


# --- Evaluation Schemas ---
class MetricRow(BaseModel):
    metric: str
    baseline: float
    target: float
    measured: float
    difference: float
    unit: str


class ErrorAnalysisItem(BaseModel):
    category: str
    count: int
    description: str
    example: str


class StakeholderRating(BaseModel):
    role: str
    question: str
    score: float
    feedback: str


class EvaluationReport(BaseModel):
    comparison_table: List[MetricRow]
    waste_avoided_amount: float
    waste_avoided_percentage: float
    recommendation_precision: float
    recommendation_coverage: float
    invalid_recommendation_count: int
    human_override_rate: float
    baseline_summary: Dict[str, Any]
    proposed_summary: Dict[str, Any]
    error_analysis: List[ErrorAnalysisItem]
    stakeholder_validation: List[StakeholderRating]
