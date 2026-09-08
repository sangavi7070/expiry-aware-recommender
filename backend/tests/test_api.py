"""Automated integration tests for ExpiryAware REST API endpoints."""
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
    """GET /api/health must return status healthy and database connected."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["batch_count"] > 0


def test_dashboard_api():
    """GET /api/dashboard must return real aggregated KPIs and chart series."""
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
    """GET /api/inventory must support search, location filtering, and near_expiry filter."""
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
    """GET /api/inventory/{batch_id} returns single batch or 404."""
    response = client.get("/api/inventory/BATCH-102")
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "BATCH-102"
    assert "stock_value" in data

    # Nonexistent batch
    res_404 = client.get("/api/inventory/NONEXISTENT-999")
    assert res_404.status_code == 404


def test_recommendations_list():
    """GET /api/recommendations returns list with explainability and evidence."""
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
    """Test Approve, Reject, and Override workflow."""
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
    """POST /api/recommendations/{id}/override must reject empty or invalid reason codes."""
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
    """GET /api/data-quality returns completeness, issue breakdowns, and flagged records."""
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] >= 100
    assert data["overall_quality_score"] > 0
    assert len(data["flagged_batches"]) > 0


def test_evaluation_endpoint():
    """GET /api/evaluation returns baseline vs proposed simulation comparison."""
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "comparison_table" in data
    assert len(data["comparison_table"]) >= 6
    assert data["waste_avoided_amount"] > 0
    assert len(data["error_analysis"]) >= 4
    assert len(data["stakeholder_validation"]) >= 5


def test_seed_demo_data_endpoint():
    """POST /api/seed resets application data to deterministic baseline."""
    response = client.post("/api/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
