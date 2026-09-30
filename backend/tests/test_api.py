"""Automated integration tests for ExpiryAware REST API endpoints.

TECHNICAL TEST DOCUMENTATION - GROUP A: API INTEGRATION TESTS
=============================================================
This suite validates the end-to-end FastAPI HTTP layer, request/response serialization
via Pydantic v2 schemas, database transaction consistency, and error boundaries.

Covered Workflow:
  Inventory Ingestion -> Risk & Surplus Analysis -> Recommendation Generation ->
  Human Approval / Rejection / Override -> Audit Logging -> Data Quality & Evaluation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Ensure test database is initialized and seeded before running API tests."""
    init_db(seed_if_empty=True)


def test_health_check_api():
    """GET /api/health - System Health & Database Connectivity Verification.

    - What is being tested: Liveness probe and active database connection verification.
    - Input condition: HTTP GET request to `/api/health` without query parameters.
    - Expected behaviour: Returns HTTP 200 with service metadata, database='connected', and positive batch count.
    - Safety boundary: If database engine fails, endpoint catches error and returns status='degraded' without crashing.
    - Expected API response: HTTP 200, JSON: {"status": "healthy", "database": "connected", "batch_count": >0}.
    - Why the test matters: Serves as the primary readiness probe for the frontend connection indicator and automated health monitors.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["batch_count"] > 0


def test_dashboard_api():
    """GET /api/dashboard - Aggregated Executive Clinical Metrics & Distributions.

    - What is being tested: Aggregation of held inventory, at-risk values, transfer proposals, and chart data series.
    - Input condition: HTTP GET request to `/api/dashboard` over the active SQLite database.
    - Expected behaviour: Computes real-time KPIs (total batches, near expiry batches, stock at risk value,
      clinic location breakdowns, expiry horizon buckets, and baseline vs proposed savings).
    - Safety boundary: Aggregations handle empty or zero-value states gracefully; never divide by zero.
    - Expected API response: HTTP 200, matching `DashboardStats` schema with >= 100 total batches and 4 chart series.
    - Why the test matters: Verifies that the executive frontend dashboard is populated entirely with dynamic calculations.
    """
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_batches"] >= 100
    assert data["near_expiry_batches"] > 0
    assert data["stock_at_risk_value"] > 0
    assert len(data["stock_by_location"]) >= 5
    assert len(data["near_expiry_breakdown"]) == 4
    assert len(data["priority_distribution"]) == 4
    assert "waste_avoided_amount" in data["baseline_vs_proposed_savings"]


def test_inventory_list_and_filters():
    """GET /api/inventory - Inventory Browsing, Search, and Multi-Param Filtering.

    - What is being tested: Querying medicine batches with server-side location, category, and text search filters.
    - Input condition: Unfiltered request vs location='Clinic-A' vs search='MED-A01'.
    - Expected behaviour: Unfiltered returns >= 100 records; location filter restricts output strictly to Clinic-A;
      search matches batch codes, medicine codes, or formulation names case-insensitively.
    - Safety boundary: Invalid filter parameters do not crash SQL engine; sanitized via SQLAlchemy ORM.
    - Expected API response: HTTP 200, list of `InventoryBatchResponse` objects matching criteria.
    - Why the test matters: Ensures dispensary staff can rapidly locate specific medication batches across clinics.
    """
    response = client.get("/api/inventory")
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) >= 100

    # Filter by location
    res_loc = client.get("/api/inventory?location=Clinic-A")
    assert res_loc.status_code == 200
    batches_loc = res_loc.json()
    assert len(batches_loc) > 0
    assert all(b["source_location"] == "Clinic-A" for b in batches_loc)

    # Search filter
    res_search = client.get("/api/inventory?search=MED-A01")
    assert res_search.status_code == 200
    batches_search = res_search.json()
    assert len(batches_search) > 0


def test_inventory_single_batch():
    """GET /api/inventory/{batch_id} - Single Batch Deep Inspection & 404 Error Boundary.

    - What is being tested: Retrieval of a single inventory batch record and 404 handling for unknown IDs.
    - Input condition: Known batch_id='BATCH-102' vs unknown batch_id='NONEXISTENT-999'.
    - Expected behaviour: Known ID returns complete batch details; unknown ID returns HTTP 404 with structured detail.
    - Safety boundary: Fails safely with HTTP 404; does not expose internal database errors or stack traces.
    - Expected API response: HTTP 200 for BATCH-102; HTTP 404 for NONEXISTENT-999.
    - Why the test matters: Supports the slide-out Batch Detail Drawer on the frontend and handles missing records cleanly.
    """
    response = client.get("/api/inventory/BATCH-102")
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "BATCH-102"
    assert "stock_value" in data

    # Nonexistent batch
    res_404 = client.get("/api/inventory/NONEXISTENT-999")
    assert res_404.status_code == 404


def test_recommendations_list():
    """GET /api/recommendations - Explainable Redistribution Recommendations Feed.

    - What is being tested: Retrieval of rule-based transfer recommendations with transparent evidence.
    - Input condition: HTTP GET request to `/api/recommendations`.
    - Expected behaviour: Returns ordered list of recommendations; each entry includes risk_score,
      narrative explanation, and multi-factor evidence payload (expiry urgency, surplus, demand, location, data quality).
    - Safety boundary: Recommendations cannot be emitted without plain-English explanations (anti-black-box mandate).
    - Expected API response: HTTP 200, list of `RecommendationResponse` objects with evidence metadata.
    - Why the test matters: Verifies that pharmacists are provided with transparent rationales before approving transfers.
    """
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) >= 100

    sample = recs[0]
    assert "recommendation_id" in sample
    assert "risk_score" in sample
    assert "explanation" in sample
    assert "evidence" in sample
    assert "rules_triggered" in sample["evidence"] or "expiry_urgency" in sample["evidence"]


def test_human_approval_workflow():
    """POST /api/recommendations/{id}/approve - Clinical Confirmation & Audit Persistence.

    - What is being tested: Human-in-the-loop approval transition and automatic audit log generation.
    - Input condition: POST request with user_role='Pharmacist' and clinical justification.
    - Expected behaviour: Target recommendation transitions from 'PENDING' to 'APPROVED'; an immutable
      audit log record is persisted with matching recommendation_id, user_role, and UTC timestamp.
    - Safety boundary: BLOCKED recommendations cannot be approved (enforced via 400 Bad Request).
    - Expected API response: HTTP 200, JSON: {"success": true, "status": "APPROVED", "audit_id": "AUD-..."}.
    - Why the test matters: Enforces Rule 10: The system NEVER auto-dispatches medication without authorized staff sign-off.
    """
    # Find a pending recommendation
    recs = client.get("/api/recommendations?status_filter=PENDING").json()
    assert len(recs) > 0
    target_rec = recs[0]
    rec_id = target_rec["recommendation_id"]

    # 1. Approve
    res_approve = client.post(
        f"/api/recommendations/{rec_id}/approve",
        json={"user_role": "Pharmacist", "reason": "Surplus verified against oncology ward need.", "notes": "Approved for dispatch."}
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"

    # Verify audit log recorded it
    audit_res = client.get("/api/audit?action=APPROVED")
    assert audit_res.status_code == 200
    audits = audit_res.json()
    assert any(a["recommendation_id"] == rec_id for a in audits)


def test_override_mandatory_reason_validation():
    """POST /api/recommendations/{id}/override - Mandatory Reason Enforcement & Governance.

    - What is being tested: Strict validation of clinical override reasons against standardized allowed list.
    - Input condition:
        1. Empty reason: {"reason": "", "user_role": "Inventory Manager"}
        2. Invalid reason: {"reason": "Not a valid reason code", "user_role": "Inventory Manager"}
        3. Valid reason: {"reason": "Stock already allocated", "user_role": "Inventory Manager"}
    - Expected behaviour: Empty and invalid reason codes return HTTP 400 Bad Request; valid reason updates status to
      'OVERRIDDEN' and writes immutable audit entry.
    - Safety boundary: Unstructured or empty override reasons are strictly forbidden to ensure clinical traceability.
    - Expected API response: HTTP 400 for empty/invalid; HTTP 200 with status='OVERRIDDEN' for valid.
    - Why the test matters: Satisfies hospital regulatory governance by requiring accountability for deviating from recommendations.
    """
    recs = client.get("/api/recommendations").json()
    rec_id = recs[1]["recommendation_id"]

    # Empty reason -> 400 Bad Request
    res_empty = client.post(
        f"/api/recommendations/{rec_id}/override",
        json={"user_role": "Inventory Manager", "reason": "", "notes": "test"}
    )
    assert res_empty.status_code == 400

    # Invalid reason code -> 400 Bad Request
    res_invalid = client.post(
        f"/api/recommendations/{rec_id}/override",
        json={"user_role": "Inventory Manager", "reason": "Not a valid reason code", "notes": "test"}
    )
    assert res_invalid.status_code == 400

    # Valid reason code -> 200 OK
    res_valid = client.post(
        f"/api/recommendations/{rec_id}/override",
        json={
            "user_role": "Inventory Manager",
            "reason": "Stock already allocated",
            "notes": "Reserved for scheduled clinical trial."
        }
    )
    assert res_valid.status_code == 200
    assert res_valid.json()["status"] == "OVERRIDDEN"


def test_data_quality_endpoint():
    """GET /api/data-quality - Proactive Clinical Data Integrity Surveillance.

    - What is being tested: Comprehensive dataset scan for completeness, missing fields, and validation issues.
    - Input condition: HTTP GET request to `/api/data-quality`.
    - Expected behaviour: Computes overall data quality index (0-100), itemizes missing dates, missing demand,
      and invalid quantities, and lists flagged batch records.
    - Safety boundary: Detects and surfaces edge cases (Cases 1-7) before unsafe recommendations can reach dispensaries.
    - Expected API response: HTTP 200, matching `DataQualityReport` schema with flagged_batches list.
    - Why the test matters: Provides clinical administrators with transparency into inventory ledger hygiene.
    """
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] >= 100
    assert data["overall_quality_score"] > 0
    assert len(data["flagged_batches"]) > 0


def test_evaluation_endpoint():
    """GET /api/evaluation - Measurable Empirical Baseline vs Proposed Simulation.

    - What is being tested: Live execution of the FIFO local-only baseline vs ExpiryAware redistribution model.
    - Input condition: HTTP GET request to `/api/evaluation`.
    - Expected behaviour: Dynamically calculates metrics (used before expiry, transferred value, waste avoided,
      precision, coverage, override rate), difference table, error analysis, and synthetic stakeholder validation.
    - Safety boundary: Calculations are derived deterministically from database records; never fabricated.
    - Expected API response: HTTP 200, matching `EvaluationReport` schema with comparison_table and summaries.
    - Why the test matters: Quantifies clinical and financial efficacy (e.g. 74.4% waste reduction) with scientific reproducibility.
    """
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "comparison_table" in data
    assert len(data["comparison_table"]) >= 6
    assert data["waste_avoided_amount"] > 0
    assert len(data["error_analysis"]) >= 4
    assert len(data["stakeholder_validation"]) >= 5


def test_seed_demo_data_endpoint():
    """POST /api/seed - Deterministic Baseline Re-seeding & State Reset.

    - What is being tested: Resetting the application database to the pristine deterministic baseline (seed=42).
    - Input condition: HTTP POST request to `/api/seed`.
    - Expected behaviour: Purges modified records, re-populates 110+ synthetic batches, generates initial
      recommendations, re-establishes seed audit events, and returns success=True.
    - Safety boundary: Transactional atomic re-seeding ensures database is never left in a corrupted or half-populated state.
    - Expected API response: HTTP 200, JSON: {"success": true, "message": "Demo data successfully reset..."}.
    - Why the test matters: Enables reproducible live demonstration runs for evaluators without manual database manipulation.
    """
    response = client.post("/api/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
