# ExpiryAware — Expiry-Aware Stock Redistribution Recommender

> **"Prevent expiry. Redistribute responsibly."**  
> *Responsible clinical inventory intelligence for temperature-sensitive specialty medicines.*

---

## 1. Project Overview

Specialty clinics and hospital outpatient dispensaries manage expensive, short-dated, and temperature-sensitive pharmaceuticals (e.g. oncology biosimilars, monoclonal antibodies, insulins, immunology infusions). Because clinical patient demand varies across geographic regions, medicine batches frequently approach their expiration dates while held as local surplus at one clinic, while a neighboring facility faces impending stockouts or high procurement costs for the exact same formulation.

Traditional inventory management operates on single-facility First-In-First-Out (**FIFO**) consumption without dynamic inter-clinic redistribution. Consequently, high-value, viable medicines expire and are discarded as clinical and financial waste while treatments elsewhere are delayed.

**ExpiryAware** is a production-grade clinical decision support system that couples an explainable, multi-factor rule engine with strict human-in-the-loop clinical governance. The system proactively analyzes batch, quantity, expiry, demand, location, and data quality metrics to recommend safe inter-facility stock transfers before medicines expire.

---

## 2. Problem Statement

1. **Premature Obsolescence**: Inventory teams discover near-expiry batches too late for consumption or logistics transfer.
2. **Siloed Consumption Models**: Local FIFO usage evaluates only local clinic demand, remaining blind to regional demand that could utilize the medicine before expiry.
3. **Black-Box AI Resistance**: Clinical staff and pharmacists rightly reject opaque machine learning algorithms that cannot justify why a specific batch should be moved.
4. **Autonomous Dispatch Hazards**: Unsupervised transfer dispatch risks sending cold-chain stock over unfeasible transit corridors or depleting supplies needed for local scheduled patients.
5. **Secondary Waste Risk**: Sending surplus stock to a recipient clinic without active patient demand merely shifts the expiration event to another facility.

---

## 3. Objectives

- **Mitigate Preventable Waste**: Proactively flag batches $\le 30$ days from expiry whose local consumption rate cannot absorb current stock.
- **Match Verified Clinical Demand**: Route surplus stock only to candidate facilities with active projected demand, strictly capped by capacity limits.
- **Provide 100% Explainable Recommendations**: Replace black-box models with a deterministic 5-factor scoring engine providing plain-English clinical rationales.
- **Enforce Human-in-the-Loop Clinical Control (Rule 10)**: Forbid autonomous execution; mandate pharmacist review (Approve, Reject, Override).
- **Ensure Full Auditability**: Persist every clinical action into an immutable SQLite audit log with timestamps, roles, and standardized rationale notes.
- **Deliver Demonstrable Empirical Value**: Quantify waste reduction against a FIFO baseline with a 100% reproducible synthetic dataset.

---

## 4. Architecture

ExpiryAware follows a decoupled, three-tier modular architecture designed for local and clinical intranet deployment:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18 + Vite 5)                    │
│  - Tailwind CSS Healthcare Design System                               │
│  - Recharts (Interactive Donut, Bar & Comparative Visualizations)      │
│  - Lucide React Iconography & Slide-out Drawers / Governance Modals    │
└────────────────────────────────────▲───────────────────────────────────┘
                                     │  JSON / REST APIs (Port 8000)
┌────────────────────────────────────▼───────────────────────────────────┐
│                       BACKEND (FastAPI + Python 3.14)                  │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │   Validation Engine   │  │   Explainable Recommendation Engine   │  │
│  │ (Fail-Closed Safety)  │  │   (Multi-Factor Mathematical Scoring) │  │
│  └───────────┬───────────┘  └───────────────────┬───────────────────┘  │
│  ┌───────────▼───────────┐  ┌───────────────────▼───────────────────┐  │
│  │ Human Action Handler  │  │     Empirical Evaluation Simulator    │  │
│  │  (Approve/Reject/Ovr) │  │    (FIFO Baseline vs ExpiryAware)     │  │
│  └───────────────────────┘  └───────────────────────────────────────┘  │
└────────────────────────────────────▲───────────────────────────────────┘
                                     │  SQLAlchemy ORM
┌────────────────────────────────────▼───────────────────────────────────┐
│                     PERSISTENCE (Embedded SQLite)                      │
│   - inventory (InventoryBatch)                                         │
│   - recommendations (Recommendation)                                   │
│   - audit_log (AuditLog)                                               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

### Backend
- **Python 3.11+** (Verified on Python 3.14.6)
- **FastAPI**: Modern, high-performance web framework for building REST APIs with automatic OpenAPI/Swagger docs.
- **Pydantic v2**: Strict data contracts, schema serialization, and input validation.
- **SQLAlchemy 2.0**: Object-Relational Mapping (ORM) connecting application logic to persistence.
- **SQLite**: Zero-configuration, transactional, serverless embedded database.
- **Pandas & NumPy**: Tabular data manipulation and mathematical simulation.
- **Pytest & FastAPI TestClient**: Automated unit and end-to-end integration testing.

### Frontend
- **React 18**: Component-based user interface library with reactive hooks.
- **Vite 5**: Next-generation frontend build tooling and development server.
- **Tailwind CSS**: Utility-first styling with custom healthcare color palettes (emerald, brand-blue, rose, amber).
- **Recharts**: Declarative SVG chart library for clinical metrics and distributions.
- **Lucide React**: Clean, accessible clinical and interface iconography.

---

## 6. Project Structure

```
expiry-aware-recommender/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Application package initialiser
│   │   ├── database.py           # SQLite connection, sessionmaker, and schema auto-creation
│   │   ├── models.py             # SQLAlchemy models (InventoryBatch, Recommendation, AuditLog)
│   │   ├── schemas.py            # Pydantic v2 request/response validation schemas
│   │   ├── validation.py         # Clinical data validation rules (VALID, WARNING, BLOCKED)
│   │   ├── recommender.py        # Explainable 5-factor scoring engine (Rules 1-10)
│   │   ├── explanation.py        # Plain-English narrative rationale generator
│   │   ├── evaluation.py         # FIFO baseline vs ExpiryAware simulation engine
│   │   ├── seed_data.py          # Deterministic synthetic inventory generator (seed=42)
│   │   └── main.py               # FastAPI application, CORS, routers, and lifecycle
│   │
│   ├── tests/
│   │   ├── test_api.py           # 10 integration tests for all REST endpoints & workflows
│   │   ├── test_recommender.py   # 8 unit tests for scoring factors, capping, and priority bands
│   │   └── test_validation.py    # 7 unit tests for clinical edge cases and safety blocks
│   │
│   ├── requirements.txt          # Python package dependencies
│   ├── run.py                    # Standalone backend server launcher (Port 8000)
│   └── expiry_aware.db           # SQLite database file (created automatically on startup)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Sticky navigation, health status badge, demo reset trigger
│   │   │   ├── Sidebar.jsx       # Clinical operations navigation tabs
│   │   │   ├── MetricCard.jsx    # Styled KPI summary cards
│   │   │   ├── BatchDetailDrawer.jsx # Slide-out inventory inspection panel
│   │   │   ├── OverrideModal.jsx # Mandatory clinical override dialog with reason code selection
│   │   │   └── ResetDemoModal.jsx # Demo data re-seed confirmation dialog
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx # Executive KPI dashboard with 4 Recharts visualizations
│   │   │   ├── InventoryPage.jsx # Searchable, sortable, paginated inventory table
│   │   │   ├── RecommendationsPage.jsx # Transfer candidate cards, scoring breakdown & actions
│   │   │   ├── EvaluationPage.jsx # Empirical baseline vs proposed experiment table & error analysis
│   │   │   ├── AuditLogPage.jsx  # Immutable governance audit trail table with filters
│   │   │   ├── DataQualityPage.jsx # Data integrity metrics and flagged record list
│   │   │   └── ResponsibleAIPage.jsx # Ethical AI governance, transparency, and safety principles
│   │   ├── services/
│   │   │   └── api.js            # Centralized API service with error handling
│   │   ├── App.jsx               # Application root, role context, and navigation router
│   │   ├── main.jsx              # React DOM mounting
│   │   └── index.css             # Tailwind base styles and healthcare badge utilities
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── data/
│   ├── synthetic_inventory.csv   # 110+ deterministic synthetic medicine batch records
│   ├── edge_cases.csv            # 7 documented failure and boundary condition cases
│   └── stakeholder_feedback.csv  # Synthetic multi-role evaluation ratings
│
├── evaluation/
│   ├── generate_report.py        # Standalone CLI report generator
│   ├── evaluation_report.json    # Exported evaluation metrics (JSON)
│   └── evaluation_report.md      # Exported evaluation metrics (Markdown)
│
├── README.md                     # Comprehensive project documentation
└── .gitignore
```

---

## 7. System Workflow

```
[Raw Inventory Input]
        │
        ▼
[Data Validation Layer] ──────► [Critical Issue: Missing Expiry / Negative Qty] ──► BLOCKED (Fail-Closed)
        │                                                                               │
        ▼ Clean Data                                                                    ▼
[Expiry Risk Analysis]                                                          Logged in Data Quality Page
        │
        ▼
[Local Consumption vs Surplus Analysis]
        │
        ▼
[Candidate Destination Demand Matching]
        │
        ▼
[Transfer Quantity Capping (Rule 8)]
        │
        ▼
[Explainable 5-Factor Scoring (0-100)]
        │
        ▼
[Uncertainty & Confidence Calibration]
        │
        ▼
[Pharmacist Decision Queue]
        │
        ├──► [Approve]   ──────► Status: APPROVED   ──► Added to Immutable Audit Log
        ├──► [Reject]    ──────► Status: REJECTED   ──► Added to Immutable Audit Log
        └──► [Override]  ──────► Mandatory Reason  ──► Status: OVERRIDDEN ──► Added to Audit Log
```

---

## 8. Recommendation Engine

Rather than relying on opaque black-box neural networks or unexplainable embeddings, ExpiryAware employs a deterministic, transparent rule engine. Clinicians can review every point contributing to the score, understand the exact physical constraints applied, and audit the mathematical derivations.

### Scoring Formula and Weights

$$\text{Risk Score} = 0.35 \times \text{Expiry} + 0.25 \times \text{Surplus} + 0.25 \times \text{Demand} + 0.10 \times \text{Location} + 0.05 \times \text{Data Quality}$$

| Scoring Factor | Weight | Clinical Rationale for Weighting |
| :--- | :---: | :--- |
| **Expiry Urgency** | **35%** | Primary driver of obsolescence risk. Batches approaching expiration have a strictly limited window before becoming a total loss. |
| **Source Surplus** | **25%** | Ensures origin facility has authentic excess beyond its own projected patient needs. Never depletes stock needed locally. |
| **Destination Demand** | **25%** | Guarantees that recipient facility has active treatments scheduled to consume the transferred formulation before expiry. |
| **Location Logistics** | **10%** | Favors short-distance regional transfers to minimize transit time, transport costs, and cold-chain temperature deviations. |
| **Data Quality** | **5%** | Penalizes incomplete or low-confidence records to discourage decision-making based on untrusted ledger entries. |

### Priority Thresholds

| Risk Score Band | Priority Classification | Operational Clinical Action |
| :---: | :--- | :--- |
| **80 – 100** | `HIGH PRIORITY` | Immediate pharmacist dispatch review required; imminent expiry risk with strong demand match. |
| **60 – 79** | `MEDIUM PRIORITY` | Active candidate for scheduled weekly inter-facility transfers. |
| **40 – 59** | `LOW PRIORITY` | Monitor local consumption; defer transfer unless local demand drops. |
| **Below 40** | `NO ACTION` | Stock will be absorbed locally or destination capacity is absent. No transfer proposed. |

---

## 9. Safety Rules (Rules 1–10)

1. **Rule 1 (Expiry Urgency Acceleration)**: If `days_to_expiry` $\le 30$ days, expiry score increases to $\ge 85$ points.
2. **Rule 2 (Surplus Detection)**: If source quantity exceeds projected local consumption ($\text{qty} > \text{days} \times \text{local\_demand}$), the difference is marked as surplus. Otherwise, surplus is 0.
3. **Rule 3 (Destination Demand Eligibility)**: Candidate facility must have verified daily demand $> 0$. Clinics with zero demand receive a demand score of 0.
4. **Rule 4 (Logistics Feasibility)**: Transfer distance $\le 100$ km earns high feasibility ($\ge 85$ pts). Long haul transit incurs distance penalties.
5. **Rule 5 (Fail-Closed Safety Block — Missing Expiry)**: If expiry date is absent or malformed, recommendation is **BLOCKED**.
6. **Rule 6 (Fail-Closed Safety Block — Non-Positive Qty)**: If quantity $\le 0$, recommendation is **BLOCKED** (physical ledger corruption).
7. **Rule 7 (Uncertainty Warning — Missing Demand)**: If destination demand is missing, confidence is reduced by 25 points and status is flagged as `WARNING`.
8. **Rule 8 (Quantity Capping — Anti-Secondary Waste)**: Transfer quantity is strictly clamped:
   $$\text{Transfer Qty} = \min(\text{Surplus Qty}, \text{Destination Capacity}, \text{Total Available Stock})$$
9. **Rule 9 (Absolute Safety Block — Expired Batch)**: Already-expired stock ($\text{days} \le 0$) is strictly **BLOCKED** from redistribution.
10. **Rule 10 (Mandatory Human Confirmation)**: System **never** executes autonomously. Transfers require authorized human sign-off.

---

## 10. Explanation and Confidence

Every recommendation generated by the engine includes complete explanatory evidence. The system never outputs an unexplained score.

### Narrative Explanation Structure
```json
{
  "recommendation_id": "REC-BATCH-102",
  "batch_id": "BATCH-102",
  "explanation": "Batch BATCH-102 (Vancomycin HCl 1g Powder IV) is recommended for transfer from Clinic-A to Clinic-B. The batch is approaching expiry (12 days remaining) with 57.0 units of surplus stock at Clinic-A. Candidate Clinic-B has active daily demand (4.5 units/day) with sufficient absorption capacity. Transit distance (24 km) is within optimal feasibility range. Confidence is HIGH CONFIDENCE (98.0%). This transfer requires clinical staff approval before dispatch.",
  "evidence": {
    "expiry_urgency": "CRITICAL (12d)",
    "source_surplus": "YES (+57 units)",
    "destination_demand": "HIGH (54 cap)",
    "distance_feasibility": "EXCELLENT (24 km)",
    "temperature_control": "Ambient (15-25°C)",
    "data_quality": "98%",
    "validation_status": "VALID"
  }
}
```

### Confidence Calibration Tiers
- **HIGH CONFIDENCE ($\ge 90\%$)**: Complete records with verified recipient demand, low transit distance, and clean date fields.
- **MEDIUM CONFIDENCE ($70\% - 89\%$)**: Standard records with minor missing optional fields or moderate transit distances.
- **LOW CONFIDENCE ($< 70\%$)**: Missing destination demand, cold-chain shipments $> 100$ km, or delivery windows $\le 7$ days.
- **BLOCKED ($0\%$)**: Critical safety constraints triggered (missing expiry date, invalid quantity, or already expired).

---

## 11. Human-in-the-Loop Workflow

In strict adherence to Responsible AI guidelines for healthcare technology, ExpiryAware acts solely as an advisory decision support system:

- **Approve**: Clinician confirms that the candidate transfer aligns with regional clinical schedules. Status transitions to `APPROVED`.
- **Reject**: Clinician rejects transfer (e.g. ward reorganization). Status transitions to `REJECTED`.
- **Override**: Clinician overrides recommendation with a mandatory standardized reason code and optional clinical notes:
  - `Demand changed`
  - `Stock already allocated`
  - `Temperature concern`
  - `Transfer not feasible`
  - `Data appears incorrect`
  - `Other`
- **Audit Logging**: Every action writes an immutable record to the SQLite database with recommendation ID, action type, staff role, standardized reason, notes, and UTC timestamp.

---

## 12. Error Boundaries & Fallback Behavior

The application is engineered to fail closed on safety violations and fail soft on non-critical uncertainty.

| Input Condition | Validation Boundary | System Response | User-Facing Status | Safety Outcome |
| :--- | :--- | :--- | :---: | :--- |
| **Missing Expiry Date** | `missing_expiry_date` flag set | Halts scoring; transfer qty = 0 | `BLOCKED` | Prevents unverified pharmaceuticals from being transferred. |
| **Negative Quantity** | `negative_quantity` flag set | Halts scoring; transfer qty = 0 | `BLOCKED` | Prevents ledger corruption and phantom shipments. |
| **Zero Quantity** | `zero_quantity` flag set | Halts scoring; transfer qty = 0 | `BLOCKED` | Prevents dispatching depleted inventory. |
| **Already Expired Stock** | `already_expired` flag set | Halts scoring; transfer qty = 0 | `BLOCKED` | Enforces regulatory ban on transferring expired drugs. |
| **Missing Destination Demand** | `missing_destination_demand` flag | Fallback baseline demand (35 pts); -25 confidence | `WARNING` | Alerts staff to missing data without hiding the batch. |
| **Excessive Distance (>150 km)** | Logistics distance evaluation | Feasibility score penalty (-20 pts if cold-chain) | Low Feasibility | Mitigates thermal exposure risks in courier transit. |
| **Near-Expiry with 0 Dest Demand** | Destination capacity evaluation | Transfer capped to 0.0 units | `NO ACTION` | Protects logistics budget from futile medicine movements. |
| **Override without Reason** | Pydantic & API validation | Rejects request with HTTP 400 Bad Request | Error Prompt | Guarantees regulatory traceability and accountability. |
| **Database Connection Error** | Health check try-catch | Catches exception; returns `degraded` | Visual Badge: Offline | Prevents server crash; guides user to check SQLite state. |

---

## 13. API Documentation

All 13 endpoints are implemented in `backend/app/main.py` using FastAPI and Pydantic v2 schemas:

| HTTP Method | API Path | Purpose | Key Inputs | Response Model | Safety & Validation Behaviour |
| :---: | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | System health & DB check | None | JSON status object | Returns `healthy` or `degraded`; never crashes. |
| `GET` | `/api/dashboard` | Executive KPIs & charts | None | `DashboardStats` | Dynamic calculations; zero hardcoded numbers. |
| `GET` | `/api/inventory` | Inventory list & filtering | `location`, `category`, `search`, `near_expiry_only`, `temp_sensitive` | `List[InventoryBatchResponse]` | SQL injection safe via ORM; case-insensitive search. |
| `GET` | `/api/inventory/{batch_id}` | Single batch inspection | `batch_id` (path) | `InventoryBatchResponse` | Returns HTTP 404 if batch ID is not found. |
| `GET` | `/api/recommendations` | Recommendations feed | `priority`, `status_filter` | `List[RecommendationResponse]` | Orders by risk score descending; includes full evidence. |
| `GET` | `/api/recommendations/{id}` | Single recommendation | `recommendation_id` (path) | `RecommendationResponse` | Returns HTTP 404 if recommendation ID is not found. |
| `POST` | `/api/recommendations/{id}/approve` | Confirm transfer | `ActionRequest` (`user_role`, `reason`, `notes`) | Status confirmation JSON | Rejects BLOCKED transfers with HTTP 400. Logs to audit. |
| `POST` | `/api/recommendations/{id}/reject` | Reject transfer | `ActionRequest` (`user_role`, `reason`, `notes`) | Status confirmation JSON | Updates status to REJECTED. Logs to audit. |
| `POST` | `/api/recommendations/{id}/override` | Clinical override | `OverrideRequest` (`user_role`, `reason`, `notes`) | Status confirmation JSON | Requires mandatory reason from allowed list. Logs to audit. |
| `GET` | `/api/audit` | Audit trail history | `action` (optional filter) | `List[AuditLogResponse]` | Ordered by timestamp descending (newest first). |
| `GET` | `/api/data-quality` | Data hygiene report | None | `DataQualityReport` | Aggregates integrity scores and lists flagged records. |
| `GET` | `/api/evaluation` | Baseline vs Proposed sim | None | `EvaluationReport` | Dynamic empirical simulation comparing FIFO vs ExpiryAware. |
| `POST` | `/api/seed` | Demo data reset | None | JSON confirmation | Resets SQLite database to deterministic baseline (seed=42). |

---

## 14. Database Schema Documentation

ExpiryAware utilizes an embedded SQLite database (`backend/expiry_aware.db`) managed via SQLAlchemy ORM models in `backend/app/models.py`.

### Table 1: `inventory` (`InventoryBatch`)
Represents individual medicine batches held at clinic dispensaries.

| Column Name | Data Type | Nullable | Primary Key | Description & Constraints |
| :--- | :--- | :---: | :---: | :--- |
| `batch_id` | String | No | Yes | Unique batch identifier (e.g. `BATCH-102`, `EDGE-001`). Indexed. |
| `medicine_code` | String | No | No | Fictional formulary code (e.g. `MED-A01`). Indexed. |
| `medicine_name` | String | No | No | Clinical trade/formulation name. |
| `medicine_category` | String | No | No | Category (Oncology, Endocrine, Immunology, Anti-Infective). Indexed. |
| `source_location` | String | No | No | Origin facility (Clinics A–E). Indexed. |
| `quantity` | Float | No | No | Total physical units held in dispensary. Must be $> 0$ for validity. |
| `unit_value` | Float | No | No | Unit acquisition cost in USD ($). |
| `expiry_date` | String | No | No | Expiration date in ISO `YYYY-MM-DD` format. |
| `avg_daily_demand` | Float | Yes | No | Projected daily consumption rate at source clinic. |
| `destination_location` | String | Yes | No | Candidate recipient facility (Clinics A–E). |
| `destination_daily_demand`| Float | Yes | No | Projected daily consumption rate at recipient clinic. |
| `transfer_distance_km` | Float | Yes | No | Road transit mileage between source and destination. |
| `temperature_sensitive` | Boolean | No | No | Cold-chain requirement (`True` = 2°C–8°C, `False` = Ambient). |
| `data_quality_score` | Float | No | No | Completeness index (0.0 – 100.0). |
| `created_at` | DateTime | No | No | Record creation timestamp (UTC). |

- **Relationships**: `recommendations` — One-to-many relationship with `Recommendation` (`cascade="all, delete-orphan"`).

---

### Table 2: `recommendations` (`Recommendation`)
Stores explainable redistribution recommendations generated by the rule engine.

| Column Name | Data Type | Nullable | Primary Key | Description & Constraints |
| :--- | :--- | :---: | :---: | :--- |
| `recommendation_id` | String | No | Yes | Unique identifier (e.g. `REC-BATCH-102`). Indexed. |
| `batch_id` | String | No | No | Foreign key referencing `inventory.batch_id`. Indexed. |
| `medicine_code` | String | No | No | Formulary identifier for quick indexing. |
| `medicine_name` | String | No | No | Formulation name displayed on transfer card. |
| `source_location` | String | No | No | Dispatching facility. |
| `destination_location` | String | No | No | Receiving facility. |
| `current_quantity` | Float | No | No | Total units available at source. |
| `recommended_transfer_quantity`| Float | No | No | Transfer quantity capped by destination demand (Rule 8). |
| `days_to_expiry` | Integer | No | No | Calculated countdown from reference date to expiry. |
| `stock_value` | Float | No | No | Total valuation of available batch stock ($). |
| `risk_score` | Float | No | No | Weighted multi-factor composite score ($0.0 - 100.0$). |
| `expiry_score` | Float | No | No | Normalized expiry urgency score ($0.0 - 100.0$). |
| `surplus_score` | Float | No | No | Normalized source surplus score ($0.0 - 100.0$). |
| `demand_score` | Float | No | No | Normalized destination demand score ($0.0 - 100.0$). |
| `location_score` | Float | No | No | Normalized distance and logistics score ($0.0 - 100.0$). |
| `data_quality_score` | Float | No | No | Ledger completeness score ($0.0 - 100.0$). |
| `priority` | String | No | No | Priority band (`HIGH PRIORITY`, `MEDIUM PRIORITY`, `LOW PRIORITY`, `NO ACTION`). Indexed. |
| `confidence` | Float | No | No | Calculated confidence percentage ($15.0 - 100.0\%$). |
| `confidence_level` | String | No | No | Categorical tier (`HIGH CONFIDENCE`, `MEDIUM CONFIDENCE`, `LOW CONFIDENCE`). |
| `status` | String | No | No | Workflow status (`PENDING`, `APPROVED`, `REJECTED`, `OVERRIDDEN`, `BLOCKED`, `WARNING`). Indexed. |
| `explanation` | Text | No | No | Plain-English clinical narrative rationale. |
| `evidence_json` | Text | No | No | Serialized JSON dictionary of scoring evidence and rule triggers. |
| `created_at` | DateTime | No | No | Recommendation timestamp (UTC). |
| `updated_at` | DateTime | No | No | Decision update timestamp (UTC). |

- **Relationships**: `batch` — Many-to-one relationship with `InventoryBatch`.

---

### Table 3: `audit_log` (`AuditLog`)
Immutable governance ledger recording every human clinical action.

| Column Name | Data Type | Nullable | Primary Key | Description & Constraints |
| :--- | :--- | :---: | :---: | :--- |
| `audit_id` | String | No | Yes | Unique audit record identifier (e.g. `AUD-20260930055213-BATCH-145`). Indexed. |
| `recommendation_id` | String | No | No | Target recommendation identifier. Indexed. |
| `batch_id` | String | Yes | No | Target batch code. |
| `action` | String | No | No | Decision type (`APPROVED`, `REJECTED`, `OVERRIDDEN`). Indexed. |
| `user_role` | String | No | No | Staff role (`Pharmacist`, `Inventory Manager`, `Clinic Administrator`, `Clinical Lead`). |
| `reason` | String | No | No | Standardized decision reason code. |
| `notes` | Text | Yes | No | Detailed clinical comments or rationale. |
| `timestamp` | DateTime | No | No | Exact UTC timestamp of clinical action. Indexed. |

---

## 15. Unit Testing Documentation

The test suite contains **25 automated tests** organized into five functional groups:

### Group A: REST API Integration Tests (`test_api.py`)
1. `test_health_check_api`: Validates system liveness probe and active SQLite connectivity.
2. `test_dashboard_api`: Verifies dynamic aggregation of KPIs and chart series with zero hardcoding.
3. `test_inventory_list_and_filters`: Tests server-side location, category, and text search filtering.
4. `test_inventory_single_batch`: Verifies single record retrieval and HTTP 404 handling on unknown batch IDs.
5. `test_recommendations_list`: Validates recommendations feed, risk score ordering, and evidence payloads.
6. `test_human_approval_workflow`: Tests pharmacist approval transition (`PENDING` $\to$ `APPROVED`) and audit persistence.
7. `test_override_mandatory_reason_validation`: Tests HTTP 400 rejection on empty or invalid override reason codes.
8. `test_data_quality_endpoint`: Verifies completeness reporting, issue breakdowns, and flagged batch tracking.
9. `test_evaluation_endpoint`: Tests dynamic FIFO baseline vs ExpiryAware empirical simulation.
10. `test_seed_demo_data_endpoint`: Tests database reset endpoint (`POST /api/seed`) back to deterministic baseline.

### Group B: Recommendation Engine Tests (`test_recommender.py`)
11. `test_rule_1_expiry_urgency`: Tests Rule 1 scoring curve acceleration for batches $\le 30$ days to expiry.
12. `test_rule_2_source_surplus_detection`: Tests Rule 2 local consumption modeling and surplus identification.
13. `test_rule_3_destination_eligibility`: Tests Rule 3 recipient clinic demand verification and capacity calculation.
14. `test_rule_4_distance_feasibility`: Tests Rule 4 logistics feasibility scoring across varying transit distances.
15. `test_case_5_rule_8_transfer_capped_to_demand`: Tests Rule 8 quantity capping to prevent secondary waste.
16. `test_case_6_long_distance_penalty`: Tests transit distance penalties and cold-chain thermal duration risks.
17. `test_case_7_high_risk_zero_destination_demand`: Tests safe fallback (0 transfer quantity) when destination demand is zero.
18. `test_priority_bands`: Tests threshold classification into `HIGH PRIORITY` ($\ge 80$), `MEDIUM`, `LOW`, and `NO ACTION`.

### Group C: Validation & Safety Block Tests (`test_validation.py`)
19. `test_valid_record`: Tests end-to-end validation for complete, valid clinical batch records.
20. `test_case_1_missing_expiry_date`: Tests fail-closed safety block (Rule 5) when expiry date is missing.
21. `test_case_2_negative_quantity`: Tests fail-closed safety block (Rule 6) on corrupted negative stock values.
22. `test_case_3_missing_destination_demand`: Tests uncertainty handling (Rule 7) via `WARNING` and confidence reduction.
23. `test_case_4_already_expired_batch`: Tests absolute prohibition (Rule 9) against redistributing expired stock.
24. `test_zero_quantity`: Tests fail-closed block on depleted (0 quantity) inventory records.
25. `test_negative_unit_value`: Tests financial boundary block on negative drug acquisition costs.

---

## 16. Edge Cases Handled

The system handles seven documented edge cases without crashing:

```
Case 1: Missing Expiry Date
Input: expiry_date = ""
Validation: Missing required field; urgency cannot be computed
System Response: Status = BLOCKED, transfer quantity = 0
Safety Outcome: Unsafe recommendation prevented; flagged in Data Quality page

Case 2: Negative Quantity
Input: quantity = -25.0
Validation: Physical impossibility / ledger corruption
System Response: Status = BLOCKED, transfer quantity = 0
Safety Outcome: Phantom courier dispatch prevented

Case 3: Missing Destination Demand
Input: destination_daily_demand = None
Validation: Incomplete recipient clinical profile
System Response: Status = WARNING, confidence reduced by 25 points
Safety Outcome: Uncertainty transparently communicated; clinical review required

Case 4: Already Expired Batch
Input: expiry_date is in the past
Validation: Expired pharmaceutical product
System Response: Status = BLOCKED, transfer quantity = 0
Safety Outcome: Prohibits illegal and unsafe transport of expired medicines

Case 5: Destination Demand < Surplus Stock
Input: surplus = 85 units, destination capacity = 30 units
Validation: Rule 8 capping rule
System Response: Transfer quantity clamped to exactly 30 units
Safety Outcome: Prevents secondary waste at recipient facility

Case 6: Excessive Transit Distance (>250 km)
Input: transfer_distance_km = 290.0, temperature_sensitive = True
Validation: Thermal hold-time boundary exceeded
System Response: Location score penalized (<20 pts), cold-chain risk flag attached
Safety Outcome: Minimizes thermal breach risks in transit

Case 7: Near-Expiry Stock with Zero Destination Demand
Input: days_to_expiry = 12, destination_daily_demand = 0.0
Validation: Recipient has no active patients for formulation
System Response: Transfer quantity = 0, priority = NO ACTION
Safety Outcome: Prevents futile transport; prompts local clinical reassessment
```

---

## 17. Evaluation Method & Measurable Results

### Simulation Methodology
To measure true clinical efficacy, ExpiryAware runs an empirical simulation comparing two operating models over the deterministic synthetic dataset:

1. **Baseline Model (FIFO Local Only)**:
   - Clinics operate in isolation.
   - Stock is consumed locally until expiry: $\text{Consumed} = \min(\text{Quantity}, \text{Days} \times \text{Source Demand})$.
   - Surplus stock that cannot be absorbed locally expires and is incinerated as waste.
2. **Proposed Model (ExpiryAware Redistribution)**:
   - Proactively identifies surplus before expiry.
   - Routes eligible surplus to regional partner clinics with verified patient demand.
   - Preserves viable stock from being discarded.

### Empirical Results (Deterministic Seed 42):
- **Baseline Expired Waste**: **$1,131,978.20**
- **Proposed Expired Waste**: **$290,300.55**
- **Net Waste Avoided (Protected Value)**: **$841,677.65** (**74.4% reduction in losses**)
- **Recommendation Coverage**: **87.3%** of eligible surplus batches successfully routed
- **Recommendation Precision**: **47.0%** strictly valid transfer proposals (excluding safety-blocked batches)
- **Human Override Rate**: **33.3%** clinical exception capture

### Synthetic Stakeholder Validation Ratings (Likert 1–5):
- Pharmacist (Understandability): **4.8 / 5.0**
- Pharmacist (Explanation Usefulness): **4.7 / 5.0**
- Inventory Manager (Workflow Practicality): **4.6 / 5.0**
- Clinic Administrator (Human Approval Appropriateness): **4.9 / 5.0**
- Responsible AI Reviewer (Uncertainty Clarity): **4.8 / 5.0**
- Responsible AI Reviewer (Human Confirmation Respect): **5.0 / 5.0**

---

## 18. Responsible AI Implementation

ExpiryAware embodies ten core Responsible AI engineering principles:

1. **Synthetic Data Only**: Operates 100% on generated batch numbers, fictional medicine codes (`MED-A01`), and synthetic clinic names. Zero patient data or PHI is ingested.
2. **Data Minimization**: Stores only operational inventory attributes necessary for logistics and clinical demand matching.
3. **Explainable Open Formula**: Replaces opaque neural networks with a formulaic scoring model whose weights and rules are fully inspectable.
4. **Evidence-Based Explanations**: Accompanies every transfer proposal with a plain-English rationale breaking down urgency, surplus, demand, logistics, and data quality.
5. **Explicit Uncertainty Communication**: Highlights missing inputs with visible `WARNING` badges and confidence score reductions.
6. **Mandatory Human-in-the-Loop Confirmation (Rule 10)**: Forbids autonomous dispatch. Transfers require explicit staff sign-off.
7. **Structured Override Governance**: Requires clinicians to select standardized reason codes and document clinical context when overriding proposals.
8. **Immutable Audit Trail**: Preserves every approval, rejection, and override in a persistent SQLite audit log.
9. **Rigorous Data Quality Validation**: Validates inputs through deterministic integrity checks before calculating transfer recommendations.
10. **Fail-Closed Safety Fallbacks**: Safely halts recommendations when critical safety boundaries are breached.

---

## 19. Installation & Run Instructions

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** installed

### Step 1: Backend Setup & Execution
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server (auto-initializes and auto-seeds SQLite database)
python run.py
```
Backend API will launch on **`http://localhost:8000`**  
Interactive Swagger API documentation: **`http://localhost:8000/docs`**

### Step 2: Frontend Setup & Execution
Open a new terminal:
```bash
cd frontend

# Install Node dependencies
npm.cmd install

# Start Vite development server
npm.cmd run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 20. Verification & Test Commands

### Run Automated Backend Tests (25/25 Passing)
```bash
cd backend
python -m pytest tests/ -v
```

### Run Frontend Production Build
```bash
cd frontend
npm.cmd run build
```

### Run CLI Evaluation Simulation Report
```bash
python evaluation/generate_report.py
```

---

## 21. Limitations & Future Improvements

### Current Limitations
- **Pairwise Routing**: Evaluates point-to-point transfers between source and candidate destination clinics; does not compute multi-hop network graphs.
- **Static Daily Demand**: Uses projected daily consumption rates rather than dynamic real-time electronic health record (EHR) prescription streams.
- **Synthetic Demonstration**: Calibrated on deterministic synthetic datasets rather than live hospital enterprise resource planning (ERP) systems.

### Future Improvements
- **Multi-Facility Transshipment Optimization**: Linear programming algorithms to optimize distribution across multi-tier hospital networks with central fulfillment hubs.
- **HL7 / FHIR Clinical Integration**: Direct integration with automated dispensing cabinets (e.g. Pyxis, Omnicell) to stream live stock levels and active orders.
- **IoT Cold-Chain Telemetry**: Live MQTT streaming from cellular temperature sensors to dynamically adjust feasibility scores while medication is in transit.
